# NavigaTech

## Introduction

NavigaTech is a comprehensive career management platform designed to help users navigate their technical career paths. The platform provides resume parsing, job recommendations, career analytics, and an AI-powered chatbot to assist with career planning and development.

## Features

- **AI-Powered Resume Parsing**: Extract skills, experience, and qualifications from uploaded resumes
- **Smart Job Recommendations**: Receive personalized job suggestions based on your profile and career goals
- **Career Path Analysis**: Visualize and plan your career trajectory with data-driven insights
- **Job Market Reports**: Get detailed reports on job market trends relevant to your skills
- **Chat Assistant**: Interact with an AI-powered assistant for career guidance and questions
- **Resume Conversion**: Easily convert between different resume formats
- **WebSocket Notifications**: Real-time updates on job matches and processing status

## Architecture

NavigaTech follows a modular, service-oriented architecture built with FastAPI and dependency injection. The backend is designed around the following core components:

### High-Level Architecture

![Architecture Diagram](architecture_diagram.md)

### Key Components

- **API Layer**: REST API endpoints organized by functionality
- **Service Layer**: Business logic implementation
- **AI Components**: Resume parsing, job recommendation, and chatbot engines
- **Data Layer**: Repository pattern for data access
- **External Systems**: PostgreSQL, MongoDB, Qdrant Vector DB, Elasticsearch, S3, Kafka

### Core Workflows

1. **Resume Processing**:
   - User uploads resume to S3
   - Resume parser extracts information using NLP models
   - Information is stored and used for recommendations

2. **Job Recommendations**:
   - System analyzes user skills and experience
   - Matches with job market data
   - Provides personalized job recommendations using ML ranking algorithms

3. **Chat Support**:
   - AI-powered chatbot for career guidance
   - Leverages user data for personalized responses
   - Uses LLM models for natural language understanding

4. **Job Analytics**:
   - Generates reports on job market trends
   - Analyzes user career trajectory
   - Provides insights on skill gaps and opportunities

## Technologies Used

### Backend Stack

- **Framework**: FastAPI with Starlette and Uvicorn
- **Dependency Injection**: dependency-injector
- **Authentication**: JWT with Python-JOSE and Passlib
- **API Documentation**: OpenAPI with Swagger and ReDoc

### Databases and Storage

- **SQL Database**: PostgreSQL with SQLAlchemy and SQLModel
- **NoSQL Database**: MongoDB with PyMongo and Motor (async)
- **Vector Database**: Qdrant Client for similarity search
- **Search Engine**: Elasticsearch
- **Object Storage**: AWS S3 via Boto3
- **Message Broker**: Kafka with kafka-python
- **Caching**: Redis

### AI and Machine Learning

- **NLP/ML Frameworks**:
  - HuggingFace Transformers and Sentence-Transformers
  - LlamaIndex for document indexing and retrieval
  - OpenAI integration
  - PyTorch
  - scikit-learn

- **PDF Processing**:
  - PyMuPDF
  - pdfminer
  - pypdf

### Infrastructure

- **Containerization**: Docker and Docker Compose
- **Database Migrations**: Alembic
- **Logging**: Loguru
- **Environment Variables**: python-dotenv

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 
- MongoDB
- Elasticsearch
- Kafka
- Redis
- Docker and Docker Compose (optional)

### Environment Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with the following variables (adjust as needed):
   ```
   # API and general settings
   PROJECT_NAME=NavigaTech
   API=/api
   API_V1_STR=/v1
   BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
   
   # Database connections
   DATABASE_URI=postgresql://local:local@localhost:5432/local
   REPLICA_DATABASE_URI=postgresql://local:local@localhost:5433/local
   MONGO_DB_URI=mongodb://localhost:27017
   MONGO_DB_NAME=navigatech
   
   # External services
   ELASTICSEARCH_URL=http://localhost:9200
   QDRANT_URL=http://localhost:6333
   QDRANT_API_TOKEN=
   
   # S3 configuration
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_KEY=
   
   # Security
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # AI API keys
   OPENAI_API_KEY=
   HUGGINGFACE_API_KEY=
   ```

### Database Setup

1. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Running the Application

#### Development Mode

```bash
python run.py
```

The application will be available at http://localhost:8000

#### Docker Deployment

The project includes a complete Docker Compose setup with all required services:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL primary and replica databases
- Elasticsearch
- Redis
- Kafka and Kafka UI
- The NavigaTech application

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main API Endpoints

- `/api/v1/auth`: Authentication endpoints
- `/api/v1/users`: User management
- `/api/v1/jobs`: Job listing and management
- `/api/v1/job-analysis`: Job market analysis
- `/api/v1/job-task`: Job-related tasks
- `/api/v1/chat`: Chatbot interaction
- `/api/v1/resumes`: Resume management
- `/api/v1/ws`: WebSocket endpoints for real-time updates

## Project Structure

```
backend/
├── app/                      # Main application package
│   ├── api/                  # API endpoints
│   │   ├── endpoints/        # API route handlers
│   ├── chatbot/              # Chatbot functionality
│   ├── convert/              # File conversion utilities
│   ├── core/                 # Core application components
│   │   ├── containers/       # Dependency injection containers
│   ├── exceptions/           # Exception handling
│   ├── job_report/           # Job report generation
│   ├── model/                # Data models
│   ├── recommendation/       # Recommendation engines
│   ├── repository/           # Data access repositories
│   ├── resume_building/      # Resume building functionality
│   ├── schema/               # Pydantic schemas
│   ├── services/             # Business logic services
│   ├── util/                 # Utility functions
├── migrations/               # Alembic database migrations
├── .env                      # Environment variables
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
```

## Development Guidelines

### Adding New Features

1. Create appropriate model classes in `app/model/`
2. Add repository classes in `app/repository/` for data access
3. Implement business logic in service classes in `app/services/`
4. Create API endpoints in `app/api/endpoints/`
5. Register new routes in `app/api/routes.py`
6. Register any new dependencies in the appropriate container

### Dependency Injection

The project uses the [dependency-injector](https://github.com/ets-labs/python-dependency-injector) library for managing dependencies. The main container is `ApplicationContainer` which wires up all components.

To add a new dependency:
1. Add it to the appropriate container in `app/core/containers/`
2. Wire it into the main `ApplicationContainer` if needed
3. Use `@inject` and `Depends(Provide[ApplicationContainer.services.your_service])` in endpoints

### Database Migrations

Generate new migration after model changes:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```

### Error Handling

- Create specific exception classes in `app/exceptions/errors/`
- Register exception handlers in `app/exceptions/exception_handlers.py`

### Code Style

This project follows PEP 8 coding style. Use tools like flake8 and black to maintain code quality.

## Testing

Run tests with pytest:

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[License information] 