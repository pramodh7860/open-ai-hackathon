from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from typing import Optional
import logging

from database import get_database
from models.user import User, UserResponse, UserProgress, Achievement, UserAchievement
from middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=dict)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user profile with progress and achievements"""
    try:
        # Get user progress
        progress_doc = await db.database.user_progress.find_one({
            "user_id": current_user.id
        })
        
        # Get user achievements
        achievements = []
        async for achievement_doc in db.database.user_achievements.find({
            "user_id": current_user.id
        }).sort("earned_at", -1):
            achievement_info = await db.database.achievements.find_one({
                "_id": ObjectId(achievement_doc["achievement_id"])
            })
            if achievement_info:
                achievements.append({
                    "id": str(achievement_doc["_id"]),
                    "achievement_id": str(achievement_doc["achievement_id"]),
                    "name": achievement_info["name"],
                    "description": achievement_info["description"],
                    "icon": achievement_info["icon"],
                    "xp_reward": achievement_info["xp_reward"],
                    "earned_at": achievement_doc["earned_at"]
                })
        
        user_data = {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "avatar": current_user.avatar,
            "provider": current_user.provider,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
            "progress": progress_doc,
            "achievements": achievements
        }
        
        return {
            "success": True,
            "data": {"user": user_data}
        }
        
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/profile", response_model=dict)
async def update_user_profile(
    name: Optional[str] = None,
    avatar: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update user profile"""
    try:
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        if avatar is not None:
            update_data["avatar"] = avatar
        
        # Update user
        await db.database.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": update_data}
        )
        
        # Get updated user
        user_doc = await db.database.users.find_one({"_id": ObjectId(current_user.id)})
        user = UserResponse(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc["name"],
            avatar=user_doc.get("avatar"),
            provider=user_doc.get("provider", "email"),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": {"user": user}
        }
        
    except Exception as e:
        logger.error(f"Update user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/dashboard", response_model=dict)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user dashboard data"""
    try:
        # Get user progress
        progress_doc = await db.database.user_progress.find_one({
            "user_id": current_user.id
        })
        
        # Get today's tasks
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today.replace(day=today.day + 1)
        
        today_tasks = []
        async for task_doc in db.database.study_tasks.find({
            "user_id": current_user.id,
            "date": {"$gte": today, "$lt": tomorrow}
        }).sort("time", 1):
            today_tasks.append({
                "id": str(task_doc["_id"]),
                "subject": task_doc["subject"],
                "topic": task_doc["topic"],
                "duration": task_doc["duration"],
                "priority": task_doc["priority"],
                "status": task_doc["status"],
                "time": task_doc["time"]
            })
        
        # Get weekly progress (last 7 days)
        week_ago = today.replace(day=today.day - 7)
        pipeline = [
            {"$match": {
                "user_id": current_user.id,
                "status": "COMPLETED",
                "date": {"$gte": week_ago}
            }},
            {"$group": {
                "_id": "$subject",
                "count": {"$sum": 1},
                "total_duration": {"$sum": "$duration"}
            }}
        ]
        weekly_progress = await db.database.study_tasks.aggregate(pipeline).to_list(None)
        
        # Get recent summaries
        recent_summaries = []
        async for summary_doc in db.database.summaries.find({
            "user_id": current_user.id
        }).sort("created_at", -1).limit(3):
            recent_summaries.append({
                "id": str(summary_doc["_id"]),
                "title": summary_doc["title"],
                "original_length": summary_doc["original_length"],
                "summary_length": summary_doc["summary_length"],
                "type": summary_doc["type"],
                "created_at": summary_doc["created_at"]
            })
        
        # Get recent quiz results
        recent_quizzes = []
        async for result_doc in db.database.quiz_results.find({
            "user_id": current_user.id
        }).sort("completed_at", -1).limit(3):
            quiz_doc = await db.database.quizzes.find_one({
                "_id": ObjectId(result_doc["quiz_id"])
            })
            if quiz_doc:
                recent_quizzes.append({
                    "id": str(result_doc["_id"]),
                    "quiz_id": result_doc["quiz_id"],
                    "score": result_doc["score"],
                    "completed_at": result_doc["completed_at"],
                    "quiz_title": quiz_doc["title"],
                    "quiz_subject": quiz_doc["subject"]
                })
        
        # Get recent chat sessions
        recent_chats = []
        async for session_doc in db.database.chat_sessions.find({
            "user_id": current_user.id
        }).sort("updated_at", -1).limit(3):
            recent_chats.append({
                "id": str(session_doc["_id"]),
                "title": session_doc["title"],
                "subject": session_doc["subject"],
                "updated_at": session_doc["updated_at"]
            })
        
        # Calculate stats
        study_streak = progress_doc["study_streak"] if progress_doc else 0
        
        # Calculate total hours today
        total_hours_today = sum(task["duration"] for task in today_tasks if task["status"] == "COMPLETED") / 60
        
        quizzes_completed = progress_doc["quizzes_completed"] if progress_doc else 0
        overall_progress = progress_doc["average_score"] if progress_doc else 0
        
        return {
            "success": True,
            "data": {
                "user": {
                    "id": current_user.id,
                    "name": current_user.name,
                    "email": current_user.email,
                    "avatar": current_user.avatar
                },
                "stats": {
                    "studyStreak": study_streak,
                    "totalHoursToday": round(total_hours_today, 2),
                    "quizzesCompleted": quizzes_completed,
                    "overallProgress": round(overall_progress, 2)
                },
                "todayTasks": today_tasks,
                "weeklyProgress": weekly_progress,
                "recentSummaries": recent_summaries,
                "recentQuizzes": recent_quizzes,
                "recentChats": recent_chats
            }
        }
        
    except Exception as e:
        logger.error(f"Get dashboard data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/achievements", response_model=dict)
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user achievements"""
    try:
        # Get all achievements
        all_achievements = []
        async for achievement_doc in db.database.achievements.find().sort("xp_reward", -1):
            all_achievements.append({
                "id": str(achievement_doc["_id"]),
                "name": achievement_doc["name"],
                "description": achievement_doc["description"],
                "icon": achievement_doc["icon"],
                "xp_reward": achievement_doc["xp_reward"],
                "condition": achievement_doc["condition"],
                "created_at": achievement_doc["created_at"]
            })
        
        # Get user achievements
        user_achievement_ids = set()
        async for user_achievement_doc in db.database.user_achievements.find({
            "user_id": current_user.id
        }):
            user_achievement_ids.add(str(user_achievement_doc["achievement_id"]))
        
        # Mark which achievements are earned
        achievements_with_status = []
        for achievement in all_achievements:
            is_earned = achievement["id"] in user_achievement_ids
            earned_at = None
            
            if is_earned:
                user_achievement_doc = await db.database.user_achievements.find_one({
                    "user_id": current_user.id,
                    "achievement_id": achievement["id"]
                })
                if user_achievement_doc:
                    earned_at = user_achievement_doc["earned_at"]
            
            achievements_with_status.append({
                **achievement,
                "earned": is_earned,
                "earned_at": earned_at
            })
        
        return {
            "success": True,
            "data": {
                "achievements": achievements_with_status,
                "earnedCount": len(user_achievement_ids),
                "totalCount": len(all_achievements)
            }
        }
        
    except Exception as e:
        logger.error(f"Get user achievements error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/account", response_model=dict)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete user account and all related data"""
    try:
        user_id = current_user.id
        
        # Delete all user data
        await db.database.users.delete_one({"_id": ObjectId(user_id)})
        await db.database.user_progress.delete_one({"user_id": user_id})
        await db.database.study_tasks.delete_many({"user_id": user_id})
        await db.database.summaries.delete_many({"user_id": user_id})
        await db.database.quizzes.delete_many({"user_id": user_id})
        await db.database.quiz_results.delete_many({"user_id": user_id})
        await db.database.chat_sessions.delete_many({"user_id": user_id})
        await db.database.user_achievements.delete_many({"user_id": user_id})
        
        # Delete questions for user's quizzes
        user_quiz_ids = []
        async for quiz_doc in db.database.quizzes.find({"user_id": user_id}):
            user_quiz_ids.append(str(quiz_doc["_id"]))
        
        if user_quiz_ids:
            await db.database.questions.delete_many({"quiz_id": {"$in": user_quiz_ids}})
        
        # Delete messages for user's chat sessions
        user_session_ids = []
        async for session_doc in db.database.chat_sessions.find({"user_id": user_id}):
            user_session_ids.append(str(session_doc["_id"]))
        
        if user_session_ids:
            await db.database.chat_messages.delete_many({"session_id": {"$in": user_session_ids}})
        
        return {
            "success": True,
            "message": "Account deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete account error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

