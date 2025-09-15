from fastapi import APIRouter, HTTPException, Depends, status, Query
from datetime import datetime
from bson import ObjectId
from typing import Optional, List
import logging

from database import get_database
from models.quiz import Quiz, QuizCreate, QuizResponse, QuizSubmission, QuizResult, QuizResultResponse, Question, QuestionType, Difficulty
from models.user import User
from middleware.auth import get_current_user
from services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=dict)
async def get_quizzes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    subject: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all quizzes for a user"""
    try:
        # Build query
        query = {"user_id": current_user.id, "is_active": True}
        
        if subject:
            query["subject"] = {"$regex": subject, "$options": "i"}
        if difficulty:
            query["difficulty"] = difficulty
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get quizzes with questions count
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "questions",
                "localField": "_id",
                "foreignField": "quiz_id",
                "as": "questions"
            }},
            {"$lookup": {
                "from": "quiz_results",
                "localField": "_id",
                "foreignField": "quiz_id",
                "as": "results"
            }},
            {"$addFields": {
                "question_count": {"$size": "$questions"},
                "result_count": {"$size": "$results"}
            }},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        quizzes = []
        async for quiz_doc in db.database.quizzes.aggregate(pipeline):
            quizzes.append({
                "id": str(quiz_doc["_id"]),
                "user_id": quiz_doc["user_id"],
                "title": quiz_doc["title"],
                "subject": quiz_doc["subject"],
                "topic": quiz_doc.get("topic"),
                "description": quiz_doc.get("description"),
                "time_limit": quiz_doc["time_limit"],
                "difficulty": quiz_doc["difficulty"],
                "is_active": quiz_doc["is_active"],
                "created_at": quiz_doc["created_at"],
                "updated_at": quiz_doc["updated_at"],
                "question_count": quiz_doc["question_count"],
                "result_count": quiz_doc["result_count"]
            })
        
        # Get total count
        total = await db.database.quizzes.count_documents(query)
        
        return {
            "success": True,
            "data": {
                "quizzes": quizzes,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get quizzes error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{quiz_id}", response_model=dict)
async def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get a specific quiz with questions"""
    try:
        # Get quiz
        quiz_doc = await db.database.quizzes.find_one({
            "_id": ObjectId(quiz_id),
            "user_id": current_user.id
        })
        
        if not quiz_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Get questions
        questions = []
        async for question_doc in db.database.questions.find({"quiz_id": quiz_id}).sort("order", 1):
            questions.append({
                "id": str(question_doc["_id"]),
                "type": question_doc["type"],
                "question": question_doc["question"],
                "options": question_doc.get("options", []),
                "correct_answer": question_doc["correct_answer"],
                "explanation": question_doc["explanation"],
                "difficulty": question_doc["difficulty"],
                "topic": question_doc.get("topic"),
                "order": question_doc["order"]
            })
        
        quiz = {
            "id": str(quiz_doc["_id"]),
            "user_id": quiz_doc["user_id"],
            "title": quiz_doc["title"],
            "subject": quiz_doc["subject"],
            "topic": quiz_doc.get("topic"),
            "description": quiz_doc.get("description"),
            "time_limit": quiz_doc["time_limit"],
            "difficulty": quiz_doc["difficulty"],
            "is_active": quiz_doc["is_active"],
            "created_at": quiz_doc["created_at"],
            "updated_at": quiz_doc["updated_at"],
            "questions": questions
        }
        
        return {
            "success": True,
            "data": {"quiz": quiz}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=dict)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new quiz with AI-generated questions"""
    try:
        # Generate AI quiz questions
        generated_questions = await ai_service.generate_quiz_questions(
            quiz_data.content or f"General knowledge about {quiz_data.subject}{f' - {quiz_data.topic}' if quiz_data.topic else ''}",
            quiz_data.subject,
            quiz_data.topic or quiz_data.subject,
            quiz_data.num_questions,
            quiz_data.difficulty,
            quiz_data.question_types
        )
        
        # Create quiz document
        quiz_doc = {
            "user_id": current_user.id,
            "title": quiz_data.title,
            "subject": quiz_data.subject,
            "topic": quiz_data.topic,
            "description": quiz_data.description,
            "time_limit": quiz_data.time_limit,
            "difficulty": quiz_data.difficulty.value,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert quiz
        quiz_result = await db.database.quizzes.insert_one(quiz_doc)
        quiz_id = str(quiz_result.inserted_id)
        
        # Create questions
        questions = []
        for i, q in enumerate(generated_questions):
            question_doc = {
                "quiz_id": quiz_id,
                "type": q["type"].upper(),
                "question": q["question"],
                "options": q.get("options", []),
                "correct_answer": str(q["correctAnswer"]),
                "explanation": q["explanation"],
                "difficulty": q["difficulty"].upper(),
                "topic": q.get("topic", quiz_data.topic),
                "order": i + 1,
                "created_at": datetime.utcnow()
            }
            
            question_result = await db.database.questions.insert_one(question_doc)
            questions.append({
                "id": str(question_result.inserted_id),
                "type": question_doc["type"],
                "question": question_doc["question"],
                "options": question_doc["options"],
                "correct_answer": question_doc["correct_answer"],
                "explanation": question_doc["explanation"],
                "difficulty": question_doc["difficulty"],
                "topic": question_doc["topic"],
                "order": question_doc["order"]
            })
        
        return {
            "success": True,
            "message": "Quiz created successfully",
            "data": {
                "quiz": {
                    "id": quiz_id,
                    "user_id": current_user.id,
                    "title": quiz_data.title,
                    "subject": quiz_data.subject,
                    "topic": quiz_data.topic,
                    "description": quiz_data.description,
                    "time_limit": quiz_data.time_limit,
                    "difficulty": quiz_data.difficulty.value,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "questions": questions
            }
        }
        
    except Exception as e:
        logger.error(f"Create quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quiz"
        )

@router.post("/{quiz_id}/submit", response_model=dict)
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Submit quiz answers and get results"""
    try:
        # Get quiz with questions
        quiz_doc = await db.database.quizzes.find_one({
            "_id": ObjectId(quiz_id),
            "user_id": current_user.id
        })
        
        if not quiz_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Get questions
        questions = []
        async for question_doc in db.database.questions.find({"quiz_id": quiz_id}).sort("order", 1):
            questions.append(question_doc)
        
        # Calculate score
        correct_answers = 0
        results = []
        
        for question in questions:
            user_answer = next((a for a in submission.answers if a["questionId"] == str(question["_id"])), None)
            is_correct = user_answer and str(user_answer["answer"]) == str(question["correct_answer"])
            
            if is_correct:
                correct_answers += 1
            
            results.append({
                "questionId": str(question["_id"]),
                "userAnswer": user_answer["answer"] if user_answer else "",
                "isCorrect": is_correct,
                "timeSpent": user_answer["timeSpent"] if user_answer else 0
            })
        
        score = round((correct_answers / len(questions)) * 100) if questions else 0
        
        # Save quiz result
        result_doc = {
            "user_id": current_user.id,
            "quiz_id": quiz_id,
            "score": score,
            "total_time": submission.time_spent,
            "completed_at": datetime.utcnow()
        }
        
        result = await db.database.quiz_results.insert_one(result_doc)
        
        # Update user progress
        await update_user_progress(current_user.id, score, db)
        
        return {
            "success": True,
            "message": "Quiz submitted successfully",
            "data": {
                "quizResult": {
                    "id": str(result.inserted_id),
                    "user_id": current_user.id,
                    "quiz_id": quiz_id,
                    "score": score,
                    "total_time": submission.time_spent,
                    "completed_at": datetime.utcnow()
                },
                "score": score,
                "correctAnswers": correct_answers,
                "totalQuestions": len(questions),
                "results": results
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit quiz"
        )

@router.get("/{quiz_id}/results", response_model=dict)
async def get_quiz_results(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get quiz results/history"""
    try:
        results = []
        async for result_doc in db.database.quiz_results.find({
            "quiz_id": quiz_id,
            "user_id": current_user.id
        }).sort("completed_at", -1):
            results.append({
                "id": str(result_doc["_id"]),
                "user_id": result_doc["user_id"],
                "quiz_id": result_doc["quiz_id"],
                "score": result_doc["score"],
                "total_time": result_doc["total_time"],
                "completed_at": result_doc["completed_at"]
            })
        
        return {
            "success": True,
            "data": {"results": results}
        }
        
    except Exception as e:
        logger.error(f"Get quiz results error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{quiz_id}", response_model=dict)
async def delete_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a quiz (soft delete)"""
    try:
        # Check if quiz exists and belongs to user
        existing_quiz = await db.database.quizzes.find_one({
            "_id": ObjectId(quiz_id),
            "user_id": current_user.id
        })
        
        if not existing_quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Soft delete by setting is_active to False
        await db.database.quizzes.update_one(
            {"_id": ObjectId(quiz_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": "Quiz deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/stats/overview", response_model=dict)
async def get_quiz_stats(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get quiz statistics overview"""
    try:
        # Get various statistics
        total_quizzes = await db.database.quizzes.count_documents({
            "user_id": current_user.id,
            "is_active": True
        })
        
        total_attempts = await db.database.quiz_results.count_documents({
            "user_id": current_user.id
        })
        
        # Get average score
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {"_id": None, "average_score": {"$avg": "$score"}}}
        ]
        result = await db.database.quiz_results.aggregate(pipeline).to_list(1)
        average_score = round(result[0]["average_score"], 2) if result else 0
        
        # Get quizzes by subject
        pipeline = [
            {"$match": {"user_id": current_user.id, "is_active": True}},
            {"$group": {"_id": "$subject", "count": {"$sum": 1}}}
        ]
        quizzes_by_subject = await db.database.quizzes.aggregate(pipeline).to_list(None)
        
        # Get recent results
        recent_results = []
        async for result_doc in db.database.quiz_results.find({
            "user_id": current_user.id
        }).sort("completed_at", -1).limit(5):
            # Get quiz title
            quiz_doc = await db.database.quizzes.find_one({"_id": ObjectId(result_doc["quiz_id"])})
            recent_results.append({
                "id": str(result_doc["_id"]),
                "quiz_id": result_doc["quiz_id"],
                "score": result_doc["score"],
                "total_time": result_doc["total_time"],
                "completed_at": result_doc["completed_at"],
                "quiz_title": quiz_doc["title"] if quiz_doc else "Unknown Quiz",
                "quiz_subject": quiz_doc["subject"] if quiz_doc else "Unknown"
            })
        
        return {
            "success": True,
            "data": {
                "totalQuizzes": total_quizzes,
                "totalAttempts": total_attempts,
                "averageScore": average_score,
                "quizzesBySubject": quizzes_by_subject,
                "recentResults": recent_results
            }
        }
        
    except Exception as e:
        logger.error(f"Get quiz stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def update_user_progress(user_id: str, score: int, db):
    """Update user progress after quiz completion"""
    try:
        progress_doc = await db.database.user_progress.find_one({"user_id": user_id})
        
        if progress_doc:
            new_quizzes_completed = progress_doc["quizzes_completed"] + 1
            new_total_score = (progress_doc["average_score"] * progress_doc["quizzes_completed"] + score) / new_quizzes_completed
            
            await db.database.user_progress.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "quizzes_completed": new_quizzes_completed,
                        "average_score": round(new_total_score, 2),
                        "last_active_date": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
    except Exception as e:
        logger.error(f"Update user progress error: {e}")

