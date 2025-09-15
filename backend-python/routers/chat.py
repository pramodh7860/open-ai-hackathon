from fastapi import APIRouter, HTTPException, Depends, status, Query
from datetime import datetime
from bson import ObjectId
from typing import Optional, List
import logging

from database import get_database
from models.chat import ChatSession, ChatMessage, ChatSessionCreate, ChatMessageCreate, ChatMessageRate, ChatSessionResponse, ChatMessageResponse, MessageType
from models.user import User
from middleware.auth import get_current_user
from services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/sessions", response_model=dict)
async def get_chat_sessions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    subject: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all chat sessions for a user"""
    try:
        # Build query
        query = {"user_id": current_user.id}
        
        if subject:
            query["subject"] = subject
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get sessions with last message
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "chat_messages",
                "localField": "_id",
                "foreignField": "session_id",
                "as": "messages"
            }},
            {"$addFields": {
                "last_message": {"$arrayElemAt": ["$messages", -1]},
                "message_count": {"$size": "$messages"}
            }},
            {"$sort": {"updated_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        sessions = []
        async for session_doc in db.database.chat_sessions.aggregate(pipeline):
            last_message = session_doc.get("last_message", {})
            sessions.append({
                "id": str(session_doc["_id"]),
                "user_id": session_doc["user_id"],
                "title": session_doc["title"],
                "subject": session_doc["subject"],
                "created_at": session_doc["created_at"],
                "updated_at": session_doc["updated_at"],
                "last_message": last_message.get("content", "No messages yet"),
                "last_message_time": last_message.get("created_at", session_doc["created_at"]),
                "message_count": session_doc["message_count"]
            })
        
        # Get total count
        total = await db.database.chat_sessions.count_documents(query)
        
        return {
            "success": True,
            "data": {
                "sessions": sessions,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get chat sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/sessions/{session_id}", response_model=dict)
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get a specific chat session with messages"""
    try:
        # Get session
        session_doc = await db.database.chat_sessions.find_one({
            "_id": ObjectId(session_id),
            "user_id": current_user.id
        })
        
        if not session_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get messages
        messages = []
        async for message_doc in db.database.chat_messages.find({
            "session_id": session_id
        }).sort("created_at", 1):
            messages.append({
                "id": str(message_doc["_id"]),
                "session_id": message_doc["session_id"],
                "type": message_doc["type"],
                "content": message_doc["content"],
                "subject": message_doc.get("subject"),
                "helpful": message_doc.get("helpful"),
                "attachments": message_doc.get("attachments", []),
                "created_at": message_doc["created_at"]
            })
        
        session = {
            "id": str(session_doc["_id"]),
            "user_id": session_doc["user_id"],
            "title": session_doc["title"],
            "subject": session_doc["subject"],
            "created_at": session_doc["created_at"],
            "updated_at": session_doc["updated_at"],
            "messages": messages
        }
        
        return {
            "success": True,
            "data": {"session": session}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/sessions", response_model=dict)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new chat session"""
    try:
        session_doc = {
            "user_id": current_user.id,
            "title": session_data.title,
            "subject": session_data.subject,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.database.chat_sessions.insert_one(session_doc)
        session_id = str(result.inserted_id)
        
        session = {
            "id": session_id,
            "user_id": current_user.id,
            "title": session_data.title,
            "subject": session_data.subject,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "message": "Chat session created successfully",
            "data": {"session": session}
        }
        
    except Exception as e:
        logger.error(f"Create chat session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/sessions/{session_id}/messages", response_model=dict)
async def send_message(
    session_id: str,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Send a message to a chat session"""
    try:
        # Verify session exists and belongs to user
        session_doc = await db.database.chat_sessions.find_one({
            "_id": ObjectId(session_id),
            "user_id": current_user.id
        })
        
        if not session_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Create user message
        user_message_doc = {
            "session_id": session_id,
            "type": MessageType.USER.value,
            "content": message_data.content,
            "subject": message_data.subject or session_doc["subject"],
            "attachments": message_data.attachments,
            "created_at": datetime.utcnow()
        }
        
        user_result = await db.database.chat_messages.insert_one(user_message_doc)
        user_message = {
            "id": str(user_result.inserted_id),
            "session_id": session_id,
            "type": MessageType.USER.value,
            "content": message_data.content,
            "subject": message_data.subject or session_doc["subject"],
            "attachments": message_data.attachments,
            "created_at": datetime.utcnow()
        }
        
        # Generate AI response
        try:
            # Get recent conversation history for context
            recent_messages = []
            async for msg_doc in db.database.chat_messages.find({
                "session_id": session_id
            }).sort("created_at", -1).limit(10):
                recent_messages.append({
                    "role": "user" if msg_doc["type"] == "USER" else "assistant",
                    "content": msg_doc["content"]
                })
            
            # Reverse to get chronological order
            recent_messages.reverse()
            
            ai_response = await ai_service.generate_chat_response(
                message_data.content,
                session_doc["subject"],
                recent_messages
            )
            
            # Create bot message
            bot_message_doc = {
                "session_id": session_id,
                "type": MessageType.BOT.value,
                "content": ai_response,
                "subject": session_doc["subject"],
                "created_at": datetime.utcnow()
            }
            
            bot_result = await db.database.chat_messages.insert_one(bot_message_doc)
            bot_message = {
                "id": str(bot_result.inserted_id),
                "session_id": session_id,
                "type": MessageType.BOT.value,
                "content": ai_response,
                "subject": session_doc["subject"],
                "created_at": datetime.utcnow()
            }
            
        except Exception as ai_error:
            logger.error(f"AI response generation error: {ai_error}")
            
            # Create fallback response
            bot_message_doc = {
                "session_id": session_id,
                "type": MessageType.BOT.value,
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                "subject": session_doc["subject"],
                "created_at": datetime.utcnow()
            }
            
            bot_result = await db.database.chat_messages.insert_one(bot_message_doc)
            bot_message = {
                "id": str(bot_result.inserted_id),
                "session_id": session_id,
                "type": MessageType.BOT.value,
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                "subject": session_doc["subject"],
                "created_at": datetime.utcnow()
            }
        
        # Update session timestamp
        await db.database.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "data": {
                "userMessage": user_message,
                "botMessage": bot_message
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/messages/{message_id}/rate", response_model=dict)
async def rate_message(
    message_id: str,
    rating: ChatMessageRate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Rate a message helpfulness"""
    try:
        # Verify message exists and belongs to user's session
        message_doc = await db.database.chat_messages.find_one({
            "_id": ObjectId(message_id),
            "session_id": {"$in": [
                str(session["_id"]) for session in 
                await db.database.chat_sessions.find({"user_id": current_user.id}).to_list(None)
            ]}
        })
        
        if not message_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Update message rating
        await db.database.chat_messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"helpful": rating.helpful}}
        )
        
        return {
            "success": True,
            "message": "Message rating updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a chat session"""
    try:
        # Verify session exists and belongs to user
        existing_session = await db.database.chat_sessions.find_one({
            "_id": ObjectId(session_id),
            "user_id": current_user.id
        })
        
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Delete session and all messages
        await db.database.chat_sessions.delete_one({"_id": ObjectId(session_id)})
        await db.database.chat_messages.delete_many({"session_id": session_id})
        
        return {
            "success": True,
            "message": "Chat session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete chat session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/stats/overview", response_model=dict)
async def get_chat_stats(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get chat statistics overview"""
    try:
        # Get various statistics
        total_sessions = await db.database.chat_sessions.count_documents({
            "user_id": current_user.id
        })
        
        total_messages = await db.database.chat_messages.count_documents({
            "session_id": {"$in": [
                str(session["_id"]) for session in 
                await db.database.chat_sessions.find({"user_id": current_user.id}).to_list(None)
            ]},
            "type": "USER"
        })
        
        # Get messages by subject
        pipeline = [
            {"$lookup": {
                "from": "chat_sessions",
                "localField": "session_id",
                "foreignField": "_id",
                "as": "session"
            }},
            {"$unwind": "$session"},
            {"$match": {"session.user_id": current_user.id, "type": "USER"}},
            {"$group": {"_id": "$subject", "count": {"$sum": 1}}}
        ]
        messages_by_subject = await db.database.chat_messages.aggregate(pipeline).to_list(None)
        
        # Get recent sessions
        recent_sessions = []
        async for session_doc in db.database.chat_sessions.find({
            "user_id": current_user.id
        }).sort("updated_at", -1).limit(5):
            message_count = await db.database.chat_messages.count_documents({
                "session_id": str(session_doc["_id"])
            })
            
            recent_sessions.append({
                "id": str(session_doc["_id"]),
                "title": session_doc["title"],
                "subject": session_doc["subject"],
                "updated_at": session_doc["updated_at"],
                "message_count": message_count
            })
        
        return {
            "success": True,
            "data": {
                "totalSessions": total_sessions,
                "totalMessages": total_messages,
                "messagesBySubject": messages_by_subject,
                "recentSessions": recent_sessions
            }
        }
        
    except Exception as e:
        logger.error(f"Get chat stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

