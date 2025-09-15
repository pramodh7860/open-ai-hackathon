import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database() -> Database:
    """Get database instance"""
    return db

async def connect_to_mongo():
    """Create database connection"""
    try:
        # MongoDB connection string
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DATABASE", "studybuddy")
        
        db.client = AsyncIOMotorClient(mongo_url)
        db.database = db.client[db_name]
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {db_name}")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # User collection indexes
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("created_at")
        
        # Study tasks indexes
        await db.database.study_tasks.create_index("user_id")
        await db.database.study_tasks.create_index([("user_id", 1), ("date", 1)])
        await db.database.study_tasks.create_index([("user_id", 1), ("status", 1)])
        
        # Summaries indexes
        await db.database.summaries.create_index("user_id")
        await db.database.summaries.create_index([("user_id", 1), ("created_at", -1)])
        await db.database.summaries.create_index("type")
        
        # Quizzes indexes
        await db.database.quizzes.create_index("user_id")
        await db.database.quizzes.create_index([("user_id", 1), ("created_at", -1)])
        await db.database.quizzes.create_index("subject")
        
        # Questions indexes
        await db.database.questions.create_index("quiz_id")
        await db.database.questions.create_index("type")
        
        # Quiz results indexes
        await db.database.quiz_results.create_index("user_id")
        await db.database.quiz_results.create_index([("user_id", 1), ("completed_at", -1)])
        await db.database.quiz_results.create_index("quiz_id")
        
        # Chat sessions indexes
        await db.database.chat_sessions.create_index("user_id")
        await db.database.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)])
        
        # Chat messages indexes
        await db.database.chat_messages.create_index("session_id")
        await db.database.chat_messages.create_index([("session_id", 1), ("created_at", 1)])
        
        # User progress indexes
        await db.database.user_progress.create_index("user_id", unique=True)
        
        # Achievements indexes
        await db.database.achievements.create_index("name", unique=True)
        
        # User achievements indexes
        await db.database.user_achievements.create_index([("user_id", 1), ("achievement_id", 1)], unique=True)
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# Initialize database connection
async def init_database():
    await connect_to_mongo()

