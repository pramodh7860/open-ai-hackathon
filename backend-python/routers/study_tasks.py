from fastapi import APIRouter, HTTPException, Depends, status, Query
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional, List
import logging

from database import get_database
from models.study_task import StudyTask, StudyTaskCreate, StudyTaskUpdate, StudyTaskResponse
from models.user import User
from middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=dict)
async def get_study_tasks(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all study tasks for a user"""
    try:
        # Build query
        query = {"user_id": current_user.id}
        
        if date:
            date_obj = datetime.fromisoformat(date)
            start_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            query["date"] = {"$gte": start_date, "$lt": end_date}
        
        if status:
            query["status"] = status
        
        if subject:
            query["subject"] = {"$regex": subject, "$options": "i"}
        
        # Get tasks
        cursor = db.database.study_tasks.find(query).sort([("date", 1), ("time", 1)])
        tasks = []
        
        async for task_doc in cursor:
            tasks.append(StudyTaskResponse(
                id=str(task_doc["_id"]),
                user_id=task_doc["user_id"],
                subject=task_doc["subject"],
                topic=task_doc["topic"],
                description=task_doc.get("description"),
                duration=task_doc["duration"],
                priority=task_doc["priority"],
                date=task_doc["date"],
                time=task_doc["time"],
                status=task_doc["status"],
                created_at=task_doc["created_at"],
                updated_at=task_doc["updated_at"]
            ))
        
        return {
            "success": True,
            "data": {"tasks": tasks}
        }
        
    except Exception as e:
        logger.error(f"Get study tasks error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{task_id}", response_model=dict)
async def get_study_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get a specific study task"""
    try:
        task_doc = await db.database.study_tasks.find_one({
            "_id": ObjectId(task_id),
            "user_id": current_user.id
        })
        
        if not task_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study task not found"
            )
        
        task = StudyTaskResponse(
            id=str(task_doc["_id"]),
            user_id=task_doc["user_id"],
            subject=task_doc["subject"],
            topic=task_doc["topic"],
            description=task_doc.get("description"),
            duration=task_doc["duration"],
            priority=task_doc["priority"],
            date=task_doc["date"],
            time=task_doc["time"],
            status=task_doc["status"],
            created_at=task_doc["created_at"],
            updated_at=task_doc["updated_at"]
        )
        
        return {
            "success": True,
            "data": {"task": task}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get study task error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=dict)
async def create_study_task(
    task_data: StudyTaskCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new study task"""
    try:
        task_doc = {
            "user_id": current_user.id,
            "subject": task_data.subject,
            "topic": task_data.topic,
            "description": task_data.description,
            "duration": task_data.duration,
            "priority": task_data.priority.value,
            "date": task_data.date,
            "time": task_data.time,
            "status": "PENDING",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.database.study_tasks.insert_one(task_doc)
        task_id = str(result.inserted_id)
        
        # Get the created task
        task_doc = await db.database.study_tasks.find_one({"_id": ObjectId(task_id)})
        task = StudyTaskResponse(
            id=str(task_doc["_id"]),
            user_id=task_doc["user_id"],
            subject=task_doc["subject"],
            topic=task_doc["topic"],
            description=task_doc.get("description"),
            duration=task_doc["duration"],
            priority=task_doc["priority"],
            date=task_doc["date"],
            time=task_doc["time"],
            status=task_doc["status"],
            created_at=task_doc["created_at"],
            updated_at=task_doc["updated_at"]
        )
        
        return {
            "success": True,
            "message": "Study task created successfully",
            "data": {"task": task}
        }
        
    except Exception as e:
        logger.error(f"Create study task error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{task_id}", response_model=dict)
async def update_study_task(
    task_id: str,
    task_data: StudyTaskUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update a study task"""
    try:
        # Check if task exists and belongs to user
        existing_task = await db.database.study_tasks.find_one({
            "_id": ObjectId(task_id),
            "user_id": current_user.id
        })
        
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study task not found"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if task_data.subject is not None:
            update_data["subject"] = task_data.subject
        if task_data.topic is not None:
            update_data["topic"] = task_data.topic
        if task_data.description is not None:
            update_data["description"] = task_data.description
        if task_data.duration is not None:
            update_data["duration"] = task_data.duration
        if task_data.priority is not None:
            update_data["priority"] = task_data.priority.value
        if task_data.date is not None:
            update_data["date"] = task_data.date
        if task_data.time is not None:
            update_data["time"] = task_data.time
        if task_data.status is not None:
            update_data["status"] = task_data.status.value
        
        # Update task
        await db.database.study_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        
        # Get updated task
        task_doc = await db.database.study_tasks.find_one({"_id": ObjectId(task_id)})
        task = StudyTaskResponse(
            id=str(task_doc["_id"]),
            user_id=task_doc["user_id"],
            subject=task_doc["subject"],
            topic=task_doc["topic"],
            description=task_doc.get("description"),
            duration=task_doc["duration"],
            priority=task_doc["priority"],
            date=task_doc["date"],
            time=task_doc["time"],
            status=task_doc["status"],
            created_at=task_doc["created_at"],
            updated_at=task_doc["updated_at"]
        )
        
        return {
            "success": True,
            "message": "Study task updated successfully",
            "data": {"task": task}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update study task error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{task_id}", response_model=dict)
async def delete_study_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a study task"""
    try:
        # Check if task exists and belongs to user
        existing_task = await db.database.study_tasks.find_one({
            "_id": ObjectId(task_id),
            "user_id": current_user.id
        })
        
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study task not found"
            )
        
        # Delete task
        await db.database.study_tasks.delete_one({"_id": ObjectId(task_id)})
        
        return {
            "success": True,
            "message": "Study task deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete study task error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/{task_id}/toggle-status", response_model=dict)
async def toggle_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Toggle task status between pending and completed"""
    try:
        # Get current task
        task_doc = await db.database.study_tasks.find_one({
            "_id": ObjectId(task_id),
            "user_id": current_user.id
        })
        
        if not task_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study task not found"
            )
        
        # Toggle status
        new_status = "COMPLETED" if task_doc["status"] == "PENDING" else "PENDING"
        
        # Update task
        await db.database.study_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Get updated task
        task_doc = await db.database.study_tasks.find_one({"_id": ObjectId(task_id)})
        task = StudyTaskResponse(
            id=str(task_doc["_id"]),
            user_id=task_doc["user_id"],
            subject=task_doc["subject"],
            topic=task_doc["topic"],
            description=task_doc.get("description"),
            duration=task_doc["duration"],
            priority=task_doc["priority"],
            date=task_doc["date"],
            time=task_doc["time"],
            status=task_doc["status"],
            created_at=task_doc["created_at"],
            updated_at=task_doc["updated_at"]
        )
        
        return {
            "success": True,
            "message": "Task status updated successfully",
            "data": {"task": task}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Toggle task status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/stats/overview", response_model=dict)
async def get_study_stats(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get study statistics overview"""
    try:
        # Get various statistics
        total_tasks = await db.database.study_tasks.count_documents({"user_id": current_user.id})
        completed_tasks = await db.database.study_tasks.count_documents({
            "user_id": current_user.id,
            "status": "COMPLETED"
        })
        pending_tasks = await db.database.study_tasks.count_documents({
            "user_id": current_user.id,
            "status": "PENDING"
        })
        
        # Get total study hours
        pipeline = [
            {"$match": {"user_id": current_user.id, "status": "COMPLETED"}},
            {"$group": {"_id": None, "total_duration": {"$sum": "$duration"}}}
        ]
        result = await db.database.study_tasks.aggregate(pipeline).to_list(1)
        total_study_hours = (result[0]["total_duration"] / 60) if result else 0
        
        # Get tasks by subject
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {
                "_id": "$subject",
                "count": {"$sum": 1},
                "total_duration": {"$sum": "$duration"}
            }}
        ]
        tasks_by_subject = await db.database.study_tasks.aggregate(pipeline).to_list(None)
        
        # Get recent tasks
        recent_tasks = []
        cursor = db.database.study_tasks.find({"user_id": current_user.id}).sort("created_at", -1).limit(5)
        async for task_doc in cursor:
            recent_tasks.append({
                "id": str(task_doc["_id"]),
                "subject": task_doc["subject"],
                "topic": task_doc["topic"],
                "status": task_doc["status"],
                "created_at": task_doc["created_at"]
            })
        
        return {
            "success": True,
            "data": {
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks,
                "pendingTasks": pending_tasks,
                "totalStudyHours": round(total_study_hours, 2),
                "tasksBySubject": tasks_by_subject,
                "recentTasks": recent_tasks
            }
        }
        
    except Exception as e:
        logger.error(f"Get study stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

