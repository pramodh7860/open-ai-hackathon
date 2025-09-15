# StudyBuddy Backend API

A Python FastAPI backend for the StudyBuddy MVP - an AI-powered study assistant application.

## 🚀 Features

- **Authentication**: JWT-based authentication with Google OAuth support
- **Study Management**: CRUD operations for study tasks and progress tracking
- **AI Summarization**: OpenAI-powered text summarization with multiple formats
- **Quiz Generation**: AI-generated quizzes with various question types
- **AI Chat**: Intelligent doubt-solving chat system
- **File Upload**: Support for PDF, DOCX, and TXT file processing
- **Progress Tracking**: Comprehensive analytics and achievement system
- **MongoDB**: NoSQL database for flexible data storage

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JWT + Google OAuth
- **AI Integration**: OpenAI GPT-3.5-turbo
- **File Processing**: PyPDF2, python-docx
- **Deployment**: Docker + Docker Compose

## 📋 Prerequisites

- Python 3.11+
- MongoDB 7.0+
- OpenAI API key
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd backend-python
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=studybuddy
JWT_SECRET=your-super-secret-jwt-key
OPENAI_API_KEY=your-openai-api-key
```

### 3. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or install MongoDB locally
# Follow MongoDB installation guide for your OS
```

### 4. Run the Application

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 3001

# Production mode
uvicorn main:app --host 0.0.0.0 --port 3001
```

### 5. Seed Sample Data (Optional)

```bash
python seed_data.py
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t studybuddy-backend .

# Run container
docker run -p 3001:3001 --env-file .env studybuddy-backend
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/google` - Google OAuth
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Study Tasks
- `GET /api/study-tasks/` - Get all tasks
- `POST /api/study-tasks/` - Create task
- `GET /api/study-tasks/{id}` - Get specific task
- `PUT /api/study-tasks/{id}` - Update task
- `DELETE /api/study-tasks/{id}` - Delete task
- `PATCH /api/study-tasks/{id}/toggle-status` - Toggle task status

### Summaries
- `GET /api/summaries/` - Get all summaries
- `POST /api/summaries/` - Create summary
- `GET /api/summaries/{id}` - Get specific summary
- `PUT /api/summaries/{id}` - Update summary
- `DELETE /api/summaries/{id}` - Delete summary

### Quizzes
- `GET /api/quizzes/` - Get all quizzes
- `POST /api/quizzes/` - Create quiz
- `GET /api/quizzes/{id}` - Get quiz with questions
- `POST /api/quizzes/{id}/submit` - Submit quiz answers
- `GET /api/quizzes/{id}/results` - Get quiz results
- `DELETE /api/quizzes/{id}` - Delete quiz

### Chat
- `GET /api/chat/sessions` - Get chat sessions
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions/{id}` - Get session with messages
- `POST /api/chat/sessions/{id}/messages` - Send message
- `PATCH /api/chat/messages/{id}/rate` - Rate message
- `DELETE /api/chat/sessions/{id}` - Delete session

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile
- `GET /api/user/dashboard` - Get dashboard data
- `GET /api/user/achievements` - Get achievements
- `DELETE /api/user/account` - Delete account

### Progress Tracking
- `GET /api/progress/overview` - Get progress overview
- `GET /api/progress/study-by-subject` - Get study progress by subject
- `GET /api/progress/quiz-performance` - Get quiz performance
- `GET /api/progress/streak` - Get streak data
- `POST /api/progress/update-streak` - Update streak

### File Upload
- `POST /api/upload/file` - Upload single file
- `POST /api/upload/files` - Upload multiple files
- `GET /api/upload/supported-types` - Get supported file types

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `studybuddy` |
| `JWT_SECRET` | JWT signing secret | Required |
| `JWT_EXPIRES_IN_DAYS` | JWT expiration in days | `7` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PORT` | Server port | `3001` |
| `NODE_ENV` | Environment | `development` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `MAX_FILE_SIZE` | Max file upload size | `10485760` (10MB) |
| `UPLOAD_PATH` | Upload directory | `./uploads` |

### MongoDB Collections

- `users` - User accounts and profiles
- `study_tasks` - Study tasks and schedules
- `summaries` - AI-generated summaries
- `quizzes` - Generated quizzes
- `questions` - Quiz questions
- `quiz_results` - Quiz attempt results
- `chat_sessions` - Chat conversation sessions
- `chat_messages` - Individual chat messages
- `user_progress` - User progress and statistics
- `achievements` - Available achievements
- `user_achievements` - User earned achievements

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_auth.py
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:3001/health
```

### Logs
```bash
# Docker Compose
docker-compose logs -f backend

# Direct
tail -f logs/app.log
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- File upload restrictions
- Rate limiting (configurable)

## 🚀 Production Deployment

### Environment Setup
1. Set `NODE_ENV=production`
2. Use strong JWT secrets
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use environment-specific MongoDB
6. Configure logging and monitoring

### Performance Optimization
- Enable MongoDB connection pooling
- Implement Redis caching
- Use CDN for file uploads
- Configure load balancing
- Monitor database performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation
- Review the logs for errors

## 🔄 Updates

### Version 1.0.0
- Initial release
- Complete API implementation
- Docker support
- MongoDB integration
- OpenAI integration
- File upload support

