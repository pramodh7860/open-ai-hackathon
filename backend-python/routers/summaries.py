from fastapi import APIRouter, HTTPException, Depends, status, Query
from datetime import datetime
from bson import ObjectId
from typing import Optional
import logging

from database import get_database
from models.summary import Summary, SummaryCreate, SummaryUpdate, SummaryResponse, SummaryType
from models.user import User
from middleware.auth import get_current_user
from services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=dict)
async def get_summaries(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all summaries for a user"""
    try:
        # Build query
        query = {"user_id": current_user.id}
        
        if type:
            query["type"] = type
        if language:
            query["language"] = language
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get summaries
        cursor = db.database.summaries.find(query).sort("created_at", -1).skip(skip).limit(limit)
        summaries = []
        
        async for summary_doc in cursor:
            summaries.append(SummaryResponse(
                id=str(summary_doc["_id"]),
                user_id=summary_doc["user_id"],
                title=summary_doc["title"],
                original_text=summary_doc["original_text"],
                summary_text=summary_doc["summary_text"],
                original_length=summary_doc["original_length"],
                summary_length=summary_doc["summary_length"],
                language=summary_doc["language"],
                type=summary_doc["type"],
                created_at=summary_doc["created_at"],
                updated_at=summary_doc["updated_at"]
            ))
        
        # Get total count
        total = await db.database.summaries.count_documents(query)
        
        return {
            "success": True,
            "data": {
                "summaries": summaries,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get summaries error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{summary_id}", response_model=dict)
async def get_summary(
    summary_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get a specific summary"""
    try:
        summary_doc = await db.database.summaries.find_one({
            "_id": ObjectId(summary_id),
            "user_id": current_user.id
        })
        
        if not summary_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        summary = SummaryResponse(
            id=str(summary_doc["_id"]),
            user_id=summary_doc["user_id"],
            title=summary_doc["title"],
            original_text=summary_doc["original_text"],
            summary_text=summary_doc["summary_text"],
            original_length=summary_doc["original_length"],
            summary_length=summary_doc["summary_length"],
            language=summary_doc["language"],
            type=summary_doc["type"],
            created_at=summary_doc["created_at"],
            updated_at=summary_doc["updated_at"]
        )
        
        return {
            "success": True,
            "data": {"summary": summary}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=dict)
async def create_summary(
    summary_data: SummaryCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new summary"""
    try:
        # Generate AI summary
        summary_text = await ai_service.generate_summary(
            summary_data.original_text,
            summary_data.type,
            summary_data.language
        )
        
        # Calculate lengths
        original_length = len(summary_data.original_text.split())
        summary_length = len(summary_text.split())
        
        # Create summary document
        summary_doc = {
            "user_id": current_user.id,
            "title": summary_data.title or f"Summary {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "original_text": summary_data.original_text,
            "summary_text": summary_text,
            "original_length": original_length,
            "summary_length": summary_length,
            "language": summary_data.language,
            "type": summary_data.type.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.database.summaries.insert_one(summary_doc)
        summary_id = str(result.inserted_id)
        
        # Get the created summary
        summary_doc = await db.database.summaries.find_one({"_id": ObjectId(summary_id)})
        summary = SummaryResponse(
            id=str(summary_doc["_id"]),
            user_id=summary_doc["user_id"],
            title=summary_doc["title"],
            original_text=summary_doc["original_text"],
            summary_text=summary_doc["summary_text"],
            original_length=summary_doc["original_length"],
            summary_length=summary_doc["summary_length"],
            language=summary_doc["language"],
            type=summary_doc["type"],
            created_at=summary_doc["created_at"],
            updated_at=summary_doc["updated_at"]
        )
        
        return {
            "success": True,
            "message": "Summary created successfully",
            "data": {"summary": summary}
        }
        
    except Exception as e:
        logger.error(f"Create summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary"
        )

@router.put("/{summary_id}", response_model=dict)
async def update_summary(
    summary_id: str,
    summary_data: SummaryUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update a summary"""
    try:
        # Check if summary exists and belongs to user
        existing_summary = await db.database.summaries.find_one({
            "_id": ObjectId(summary_id),
            "user_id": current_user.id
        })
        
        if not existing_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if summary_data.title is not None:
            update_data["title"] = summary_data.title
        if summary_data.summary_text is not None:
            update_data["summary_text"] = summary_data.summary_text
            update_data["summary_length"] = len(summary_data.summary_text.split())
        
        # Update summary
        await db.database.summaries.update_one(
            {"_id": ObjectId(summary_id)},
            {"$set": update_data}
        )
        
        # Get updated summary
        summary_doc = await db.database.summaries.find_one({"_id": ObjectId(summary_id)})
        summary = SummaryResponse(
            id=str(summary_doc["_id"]),
            user_id=summary_doc["user_id"],
            title=summary_doc["title"],
            original_text=summary_doc["original_text"],
            summary_text=summary_doc["summary_text"],
            original_length=summary_doc["original_length"],
            summary_length=summary_doc["summary_length"],
            language=summary_doc["language"],
            type=summary_doc["type"],
            created_at=summary_doc["created_at"],
            updated_at=summary_doc["updated_at"]
        )
        
        return {
            "success": True,
            "message": "Summary updated successfully",
            "data": {"summary": summary}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{summary_id}", response_model=dict)
async def delete_summary(
    summary_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a summary"""
    try:
        # Check if summary exists and belongs to user
        existing_summary = await db.database.summaries.find_one({
            "_id": ObjectId(summary_id),
            "user_id": current_user.id
        })
        
        if not existing_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        # Delete summary
        await db.database.summaries.delete_one({"_id": ObjectId(summary_id)})
        
        return {
            "success": True,
            "message": "Summary deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/stats/overview", response_model=dict)
async def get_summary_stats(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get summary statistics overview"""
    try:
        # Get various statistics
        total_summaries = await db.database.summaries.count_documents({"user_id": current_user.id})
        
        # Get total words processed
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {"_id": None, "total_original_length": {"$sum": "$original_length"}}}
        ]
        result = await db.database.summaries.aggregate(pipeline).to_list(1)
        total_words_processed = result[0]["total_original_length"] if result else 0
        
        # Calculate words saved
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {"_id": None, "total_summary_length": {"$sum": "$summary_length"}}}
        ]
        result = await db.database.summaries.aggregate(pipeline).to_list(1)
        total_summary_words = result[0]["total_summary_length"] if result else 0
        words_saved = total_words_processed - total_summary_words
        time_saved = round((words_saved / 200) * 60)  # Assuming 200 words per minute reading speed
        
        # Get summaries by type
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        summaries_by_type = await db.database.summaries.aggregate(pipeline).to_list(None)
        
        # Get recent summaries
        recent_summaries = []
        cursor = db.database.summaries.find({"user_id": current_user.id}).sort("created_at", -1).limit(5)
        async for summary_doc in cursor:
            recent_summaries.append({
                "id": str(summary_doc["_id"]),
                "title": summary_doc["title"],
                "original_length": summary_doc["original_length"],
                "summary_length": summary_doc["summary_length"],
                "type": summary_doc["type"],
                "created_at": summary_doc["created_at"]
            })
        
        return {
            "success": True,
            "data": {
                "totalSummaries": total_summaries,
                "totalWordsProcessed": total_words_processed,
                "totalWordsSaved": words_saved,
                "timeSavedMinutes": time_saved,
                "summariesByType": summaries_by_type,
                "recentSummaries": recent_summaries
            }
        }
        
    except Exception as e:
        logger.error(f"Get summary stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

