from fastapi import APIRouter, HTTPException, Depends, status, Query
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional
import logging

from database import get_database
from models.user import User
from middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview", response_model=dict)
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user progress overview"""
    try:
        # Get user progress
        progress_doc = await db.database.user_progress.find_one({
            "user_id": current_user.id
        })
        
        # Get study tasks statistics
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_duration": {"$sum": "$duration"}
            }}
        ]
        study_tasks_stats = await db.database.study_tasks.aggregate(pipeline).to_list(None)
        
        # Get quiz statistics
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {
                "_id": None,
                "total_quizzes": {"$sum": 1},
                "average_score": {"$avg": "$score"},
                "total_time": {"$sum": "$total_time"}
            }}
        ]
        quiz_stats_result = await db.database.quiz_results.aggregate(pipeline).to_list(1)
        quiz_stats = quiz_stats_result[0] if quiz_stats_result else {
            "total_quizzes": 0,
            "average_score": 0,
            "total_time": 0
        }
        
        # Get summary statistics
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {
                "_id": None,
                "total_summaries": {"$sum": 1},
                "total_original_length": {"$sum": "$original_length"}
            }}
        ]
        summary_stats_result = await db.database.summaries.aggregate(pipeline).to_list(1)
        summary_stats = summary_stats_result[0] if summary_stats_result else {
            "total_summaries": 0,
            "total_original_length": 0
        }
        
        # Get chat statistics
        user_session_ids = []
        async for session_doc in db.database.chat_sessions.find({"user_id": current_user.id}):
            user_session_ids.append(str(session_doc["_id"]))
        
        total_questions = 0
        if user_session_ids:
            total_questions = await db.database.chat_messages.count_documents({
                "session_id": {"$in": user_session_ids},
                "type": "USER"
            })
        
        # Calculate additional stats
        total_study_hours = 0
        completed_tasks = 0
        for stat in study_tasks_stats:
            if stat["_id"] == "COMPLETED":
                total_study_hours = stat["total_duration"] / 60
                completed_tasks = stat["count"]
                break
        
        total_words_processed = summary_stats["total_original_length"]
        time_saved = round((total_words_processed / 200) * 60)  # Assuming 200 words per minute
        
        return {
            "success": True,
            "data": {
                "userProgress": progress_doc,
                "studyStats": {
                    "totalTasks": sum(stat["count"] for stat in study_tasks_stats),
                    "completedTasks": completed_tasks,
                    "totalStudyHours": round(total_study_hours, 2),
                    "tasksByStatus": study_tasks_stats
                },
                "quizStats": {
                    "totalQuizzes": quiz_stats["total_quizzes"],
                    "averageScore": round(quiz_stats["average_score"], 2),
                    "totalTimeSpent": quiz_stats["total_time"]
                },
                "summaryStats": {
                    "totalSummaries": summary_stats["total_summaries"],
                    "totalWordsProcessed": total_words_processed,
                    "timeSavedMinutes": time_saved
                },
                "chatStats": {
                    "totalQuestions": total_questions
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get progress overview error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/study-by-subject", response_model=dict)
async def get_study_progress_by_subject(
    period: str = Query("week", description="Time period: week, month, year"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get study progress by subject"""
    try:
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=7)
        
        # Get study progress by subject
        pipeline = [
            {"$match": {
                "user_id": current_user.id,
                "status": "COMPLETED",
                "date": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$subject",
                "count": {"$sum": 1},
                "total_duration": {"$sum": "$duration"}
            }}
        ]
        
        study_progress = await db.database.study_tasks.aggregate(pipeline).to_list(None)
        
        # Format data for frontend
        subject_stats = []
        for stat in study_progress:
            subject_stats.append({
                "subject": stat["_id"],
                "totalTasks": stat["count"],
                "completedTasks": stat["count"],  # All are completed since we filtered by status
                "totalHours": round(stat["total_duration"] / 60, 2),
                "completionRate": 100  # All are completed
            })
        
        return {
            "success": True,
            "data": {
                "period": period,
                "subjectStats": subject_stats
            }
        }
        
    except Exception as e:
        logger.error(f"Get study progress by subject error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/quiz-performance", response_model=dict)
async def get_quiz_performance(
    period: str = Query("week", description="Time period: week, month, year"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get quiz performance over time"""
    try:
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=7)
        
        # Get quiz results
        quiz_results = []
        async for result_doc in db.database.quiz_results.find({
            "user_id": current_user.id,
            "completed_at": {"$gte": start_date}
        }).sort("completed_at", 1):
            quiz_doc = await db.database.quizzes.find_one({
                "_id": ObjectId(result_doc["quiz_id"])
            })
            
            quiz_results.append({
                "id": str(result_doc["_id"]),
                "quiz_id": result_doc["quiz_id"],
                "score": result_doc["score"],
                "total_time": result_doc["total_time"],
                "completed_at": result_doc["completed_at"],
                "quiz_title": quiz_doc["title"] if quiz_doc else "Unknown Quiz",
                "quiz_subject": quiz_doc["subject"] if quiz_doc else "Unknown"
            })
        
        # Group by date for chart data
        performance_by_date = {}
        for result in quiz_results:
            date = result["completed_at"].strftime("%Y-%m-%d")
            if date not in performance_by_date:
                performance_by_date[date] = {"scores": [], "count": 0}
            performance_by_date[date]["scores"].append(result["score"])
            performance_by_date[date]["count"] += 1
        
        # Calculate average scores per date
        chart_data = []
        for date, data in performance_by_date.items():
            chart_data.append({
                "date": date,
                "averageScore": round(sum(data["scores"]) / len(data["scores"]), 2),
                "quizCount": data["count"]
            })
        
        # Calculate overall stats
        total_quizzes = len(quiz_results)
        average_score = round(sum(r["score"] for r in quiz_results) / total_quizzes, 2) if total_quizzes > 0 else 0
        
        return {
            "success": True,
            "data": {
                "period": period,
                "totalQuizzes": total_quizzes,
                "averageScore": average_score,
                "chartData": chart_data,
                "recentResults": quiz_results[-10:]  # Last 10 results
            }
        }
        
    except Exception as e:
        logger.error(f"Get quiz performance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/streak", response_model=dict)
async def get_streak_data(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get learning streak data"""
    try:
        progress_doc = await db.database.user_progress.find_one({
            "user_id": current_user.id
        })
        
        current_streak = progress_doc["study_streak"] if progress_doc else 0
        last_active_date = progress_doc["last_active_date"] if progress_doc else datetime.utcnow()
        
        # Check if user was active today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_activity = await db.database.study_tasks.find_one({
            "user_id": current_user.id,
            "date": {"$gte": today},
            "status": "COMPLETED"
        })
        
        is_active_today = today_activity is not None
        
        return {
            "success": True,
            "data": {
                "currentStreak": current_streak,
                "lastActiveDate": last_active_date,
                "isActiveToday": is_active_today,
                "longestStreak": current_streak  # This would need additional tracking in a real app
            }
        }
        
    except Exception as e:
        logger.error(f"Get streak data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/update-streak", response_model=dict)
async def update_study_streak(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update study streak (called when completing tasks)"""
    try:
        progress_doc = await db.database.user_progress.find_one({
            "user_id": current_user.id
        })
        
        if not progress_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User progress not found"
            )
        
        today = datetime.utcnow()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
        # Check if user was active yesterday
        yesterday_activity = await db.database.study_tasks.find_one({
            "user_id": current_user.id,
            "date": {"$gte": yesterday_start, "$lt": today_start},
            "status": "COMPLETED"
        })
        
        # Check if user was active today
        today_activity = await db.database.study_tasks.find_one({
            "user_id": current_user.id,
            "date": {"$gte": today_start},
            "status": "COMPLETED"
        })
        
        new_streak = progress_doc["study_streak"]
        
        if today_activity:
            # User was active today
            if yesterday_activity or progress_doc["last_active_date"].date() == yesterday_start.date():
                # Continue streak
                new_streak = progress_doc["study_streak"] + 1
            else:
                # Start new streak
                new_streak = 1
        
        # Update progress
        await db.database.user_progress.update_one(
            {"user_id": current_user.id},
            {
                "$set": {
                    "study_streak": new_streak,
                    "last_active_date": today,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Streak updated successfully",
            "data": {
                "currentStreak": new_streak,
                "lastActiveDate": today
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update streak error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

