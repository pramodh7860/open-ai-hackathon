// MongoDB initialization script
db = db.getSiblingDB('studybuddy');

// Create user for the application
db.createUser({
  user: 'studybuddy_user',
  pwd: 'studybuddy_password',
  roles: [
    {
      role: 'readWrite',
      db: 'studybuddy'
    }
  ]
});

// Create collections with initial data
db.createCollection('users');
db.createCollection('study_tasks');
db.createCollection('summaries');
db.createCollection('quizzes');
db.createCollection('questions');
db.createCollection('quiz_results');
db.createCollection('chat_sessions');
db.createCollection('chat_messages');
db.createCollection('user_progress');
db.createCollection('achievements');
db.createCollection('user_achievements');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });

db.study_tasks.createIndex({ "user_id": 1 });
db.study_tasks.createIndex({ "user_id": 1, "date": 1 });
db.study_tasks.createIndex({ "user_id": 1, "status": 1 });

db.summaries.createIndex({ "user_id": 1 });
db.summaries.createIndex({ "user_id": 1, "created_at": -1 });
db.summaries.createIndex({ "type": 1 });

db.quizzes.createIndex({ "user_id": 1 });
db.quizzes.createIndex({ "user_id": 1, "created_at": -1 });
db.quizzes.createIndex({ "subject": 1 });

db.questions.createIndex({ "quiz_id": 1 });
db.questions.createIndex({ "type": 1 });

db.quiz_results.createIndex({ "user_id": 1 });
db.quiz_results.createIndex({ "user_id": 1, "completed_at": -1 });
db.quiz_results.createIndex({ "quiz_id": 1 });

db.chat_sessions.createIndex({ "user_id": 1 });
db.chat_sessions.createIndex({ "user_id": 1, "updated_at": -1 });

db.chat_messages.createIndex({ "session_id": 1 });
db.chat_messages.createIndex({ "session_id": 1, "created_at": 1 });

db.user_progress.createIndex({ "user_id": 1 }, { unique: true });

db.achievements.createIndex({ "name": 1 }, { unique: true });

db.user_achievements.createIndex({ "user_id": 1, "achievement_id": 1 }, { unique: true });

// Insert sample achievements
db.achievements.insertMany([
  {
    name: "Study Streak Master",
    description: "Maintain a study streak for 10+ consecutive days",
    icon: "Target",
    xp_reward: 100,
    condition: '{"type": "streak", "value": 10}',
    created_at: new Date()
  },
  {
    name: "Quiz Champion",
    description: "Complete 20+ quizzes",
    icon: "Trophy",
    xp_reward: 150,
    condition: '{"type": "quizzes", "value": 20}',
    created_at: new Date()
  },
  {
    name: "Night Owl",
    description: "Study after 10 PM",
    icon: "Clock",
    xp_reward: 50,
    condition: '{"type": "time", "value": "22:00"}',
    created_at: new Date()
  },
  {
    name: "Early Bird",
    description: "Study before 7 AM",
    icon: "BookOpen",
    xp_reward: 50,
    condition: '{"type": "time", "value": "07:00"}',
    created_at: new Date()
  },
  {
    name: "Summarizer Pro",
    description: "Create 50+ summaries",
    icon: "FileText",
    xp_reward: 200,
    condition: '{"type": "summaries", "value": 50}',
    created_at: new Date()
  },
  {
    name: "Perfect Score",
    description: "Score 100% on a quiz",
    icon: "Award",
    xp_reward: 100,
    condition: '{"type": "quiz_score", "value": 100}',
    created_at: new Date()
  }
]);

print('Database initialized successfully!');

