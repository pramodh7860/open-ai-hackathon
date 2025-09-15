#!/usr/bin/env python3
"""
Seed script to populate the database with sample data
"""
import asyncio
import os
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def seed_database():
    """Seed the database with sample data"""
    # Connect to MongoDB
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DATABASE", "studybuddy")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🌱 Seeding database...")
    
    try:
        # Create demo user
        demo_user_doc = {
            "email": "demo@studybuddy.com",
            "name": "Demo Student",
            "avatar": "https://ui-avatars.com/api/?name=Demo+Student&background=3b82f6&color=fff",
            "provider": "email",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user_result = await db.users.insert_one(demo_user_doc)
        user_id = str(user_result.inserted_id)
        print(f"✅ Created demo user: {user_id}")
        
        # Create user progress
        progress_doc = {
            "user_id": user_id,
            "study_streak": 12,
            "total_hours": 156.5,
            "quizzes_completed": 24,
            "average_score": 87.5,
            "level": 5,
            "xp": 2340,
            "last_active_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.user_progress.insert_one(progress_doc)
        print("✅ Created user progress")
        
        # Create sample study tasks
        today = datetime.utcnow()
        tomorrow = today + timedelta(days=1)
        
        study_tasks = [
            {
                "user_id": user_id,
                "subject": "Mathematics",
                "topic": "Calculus - Derivatives",
                "description": "Focus on chain rule and product rule applications",
                "duration": 120,
                "priority": "HIGH",
                "date": today,
                "time": "14:00",
                "status": "PENDING",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": user_id,
                "subject": "Physics",
                "topic": "Quantum Mechanics",
                "description": "Wave-particle duality and uncertainty principle",
                "duration": 90,
                "priority": "MEDIUM",
                "date": today,
                "time": "16:00",
                "status": "COMPLETED",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": user_id,
                "subject": "Chemistry",
                "topic": "Organic Reactions",
                "description": "Substitution and elimination reactions",
                "duration": 75,
                "priority": "MEDIUM",
                "date": tomorrow,
                "time": "10:00",
                "status": "PENDING",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await db.study_tasks.insert_many(study_tasks)
        print(f"✅ Created {len(study_tasks)} study tasks")
        
        # Create sample summaries
        summaries = [
            {
                "user_id": user_id,
                "title": "Quantum Mechanics Basics",
                "original_text": "Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles. It is the foundation of all quantum physics including quantum chemistry, quantum field theory, quantum technology, and quantum information science. The theory was developed in the early 20th century to explain the behavior of matter and energy at the atomic and subatomic level.",
                "summary_text": "• Quantum mechanics describes the behavior of matter and energy at atomic and subatomic scales\n• Wave-particle duality shows that particles exhibit both wave and particle properties\n• The uncertainty principle states that position and momentum cannot be precisely determined simultaneously\n• Quantum superposition allows particles to exist in multiple states until observed\n• Quantum entanglement creates correlations between particles regardless of distance",
                "original_length": 2500,
                "summary_length": 450,
                "language": "english",
                "type": "BULLET",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": user_id,
                "title": "Photosynthesis Process",
                "original_text": "Photosynthesis is the process by which plants and other organisms use sunlight to synthesize foods with the help of chlorophyll pigments. During photosynthesis, plants take in carbon dioxide from the air and water from the soil. In the presence of sunlight, these are converted into glucose and oxygen. This process occurs in two main stages: the light-dependent reactions and the light-independent reactions (Calvin cycle).",
                "summary_text": "Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in two main stages: light-dependent reactions in the thylakoids and light-independent reactions in the stroma. During the light reactions, chlorophyll absorbs photons and splits water molecules, releasing oxygen and generating ATP and NADPH. The Calvin cycle then uses these energy carriers to fix carbon dioxide into glucose through a series of enzymatic reactions.",
                "original_length": 1800,
                "summary_length": 320,
                "language": "english",
                "type": "PARAGRAPH",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await db.summaries.insert_many(summaries)
        print(f"✅ Created {len(summaries)} summaries")
        
        # Create sample quiz
        quiz_doc = {
            "user_id": user_id,
            "title": "Calculus Fundamentals",
            "subject": "Mathematics",
            "topic": "Derivatives",
            "description": "Test your understanding of basic derivative concepts",
            "time_limit": 15,
            "difficulty": "MEDIUM",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        quiz_result = await db.quizzes.insert_one(quiz_doc)
        quiz_id = str(quiz_result.inserted_id)
        print("✅ Created sample quiz")
        
        # Create quiz questions
        questions = [
            {
                "quiz_id": quiz_id,
                "type": "MCQ",
                "question": "What is the derivative of x²?",
                "options": ["x", "2x", "x²", "2x²"],
                "correct_answer": "1",
                "explanation": "The derivative of x² is 2x using the power rule: d/dx(xⁿ) = nxⁿ⁻¹",
                "difficulty": "EASY",
                "topic": "Calculus",
                "order": 1,
                "created_at": datetime.utcnow()
            },
            {
                "quiz_id": quiz_id,
                "type": "TRUE_FALSE",
                "question": "The derivative of a constant is always zero.",
                "correct_answer": "true",
                "explanation": "This is correct. The derivative of any constant is zero because constants do not change.",
                "difficulty": "EASY",
                "topic": "Calculus",
                "order": 2,
                "created_at": datetime.utcnow()
            },
            {
                "quiz_id": quiz_id,
                "type": "MCQ",
                "question": "What is the derivative of sin(x)?",
                "options": ["cos(x)", "-cos(x)", "sin(x)", "-sin(x)"],
                "correct_answer": "0",
                "explanation": "The derivative of sin(x) is cos(x).",
                "difficulty": "MEDIUM",
                "topic": "Calculus",
                "order": 3,
                "created_at": datetime.utcnow()
            }
        ]
        
        await db.questions.insert_many(questions)
        print(f"✅ Created {len(questions)} quiz questions")
        
        # Create sample quiz result
        quiz_result_doc = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "score": 85,
            "total_time": 900,  # 15 minutes
            "completed_at": datetime.utcnow()
        }
        
        await db.quiz_results.insert_one(quiz_result_doc)
        print("✅ Created sample quiz result")
        
        # Create sample chat session
        chat_session_doc = {
            "user_id": user_id,
            "title": "Calculus Help",
            "subject": "mathematics",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        session_result = await db.chat_sessions.insert_one(chat_session_doc)
        session_id = str(session_result.inserted_id)
        print("✅ Created sample chat session")
        
        # Create sample chat messages
        messages = [
            {
                "session_id": session_id,
                "type": "USER",
                "content": "Can you explain the chain rule in calculus?",
                "subject": "mathematics",
                "created_at": datetime.utcnow()
            },
            {
                "session_id": session_id,
                "type": "BOT",
                "content": "The chain rule is a fundamental rule in calculus for finding the derivative of composite functions. If you have a function f(g(x)), the chain rule states that the derivative is f'(g(x)) × g'(x). This means you take the derivative of the outer function and multiply it by the derivative of the inner function.",
                "subject": "mathematics",
                "created_at": datetime.utcnow()
            }
        ]
        
        await db.chat_messages.insert_many(messages)
        print(f"✅ Created {len(messages)} chat messages")
        
        # Award some achievements to the demo user
        achievements = await db.achievements.find().to_list(None)
        if achievements:
            user_achievements = [
                {
                    "user_id": user_id,
                    "achievement_id": str(achievements[0]["_id"]),  # Study Streak Master
                    "earned_at": datetime.utcnow()
                },
                {
                    "user_id": user_id,
                    "achievement_id": str(achievements[1]["_id"]),  # Quiz Champion
                    "earned_at": datetime.utcnow()
                }
            ]
            
            await db.user_achievements.insert_many(user_achievements)
            print(f"✅ Awarded {len(user_achievements)} achievements to demo user")
        
        print("✅ Database seeded successfully!")
        print(f"📊 Created demo user: demo@studybuddy.com")
        print(f"📚 Created {len(study_tasks)} study tasks")
        print(f"📝 Created {len(summaries)} summaries")
        print(f"🧠 Created 1 quiz with {len(questions)} questions")
        print(f"💬 Created 1 chat session with {len(messages)} messages")
        print(f"🏆 Awarded {len(user_achievements) if 'user_achievements' in locals() else 0} achievements to demo user")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())

