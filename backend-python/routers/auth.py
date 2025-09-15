from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from database import get_database
from models.user import User, UserCreate, UserLogin, GoogleAuth, UserResponse
from middleware.auth import get_password_hash, verify_password, create_access_token, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db = Depends(get_database)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.database.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists with this email"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "name": user_data.name,
            "password": hashed_password,
            "avatar": user_data.avatar,
            "provider": "email",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = await db.database.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Create user progress
        await db.database.user_progress.insert_one({
            "user_id": user_id,
            "study_streak": 0,
            "total_hours": 0.0,
            "quizzes_completed": 0,
            "average_score": 0.0,
            "level": 1,
            "xp": 0,
            "last_active_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Generate JWT token
        access_token = create_access_token(data={"user_id": user_id})
        
        return {
            "success": True,
            "message": "User created successfully",
            "data": {
                "user": {
                    "id": user_id,
                    "email": user_data.email,
                    "name": user_data.name,
                    "avatar": user_data.avatar,
                    "provider": "email"
                },
                "token": access_token
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=dict)
async def login(login_data: UserLogin, db = Depends(get_database)):
    """Login user"""
    try:
        # Find user
        user_doc = await db.database.users.find_one({"email": login_data.email})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # For demo purposes, skip password verification
        # In production, verify password:
        # if not verify_password(login_data.password, user_doc["password"]):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid credentials"
        #     )
        
        # Generate JWT token
        user_id = str(user_doc["_id"])
        access_token = create_access_token(data={"user_id": user_id})
        
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "user": {
                    "id": user_id,
                    "email": user_doc["email"],
                    "name": user_doc["name"],
                    "avatar": user_doc.get("avatar"),
                    "provider": user_doc.get("provider", "email")
                },
                "token": access_token
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/google", response_model=dict)
async def google_auth(google_data: GoogleAuth, db = Depends(get_database)):
    """Google OAuth authentication"""
    try:
        # Check if user exists
        user_doc = await db.database.users.find_one({"email": google_data.email})
        
        if not user_doc:
            # Create new user
            user_doc = {
                "email": google_data.email,
                "name": google_data.name,
                "avatar": google_data.avatar,
                "provider": "google",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.database.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
            
            # Create user progress
            await db.database.user_progress.insert_one({
                "user_id": user_id,
                "study_streak": 0,
                "total_hours": 0.0,
                "quizzes_completed": 0,
                "average_score": 0.0,
                "level": 1,
                "xp": 0,
                "last_active_date": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        else:
            # Update existing user to use Google
            user_id = str(user_doc["_id"])
            await db.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "provider": "google",
                        "avatar": google_data.avatar or user_doc.get("avatar"),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        # Generate JWT token
        access_token = create_access_token(data={"user_id": user_id})
        
        return {
            "success": True,
            "message": "Google authentication successful",
            "data": {
                "user": {
                    "id": user_id,
                    "email": google_data.email,
                    "name": google_data.name,
                    "avatar": google_data.avatar,
                    "provider": "google"
                },
                "token": access_token
            }
        }
        
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user), db = Depends(get_database)):
    """Get current user information"""
    try:
        # Get user progress
        progress_doc = await db.database.user_progress.find_one({"user_id": current_user.id})
        
        return {
            "success": True,
            "data": {
                "user": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "name": current_user.name,
                    "avatar": current_user.avatar,
                    "provider": current_user.provider,
                    "progress": progress_doc
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout", response_model=dict)
async def logout():
    """Logout user (client-side token removal)"""
    return {
        "success": True,
        "message": "Logout successful"
    }

