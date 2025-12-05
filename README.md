<div align="center">

# 🚀 TalentPulse-AI

### *Next-Generation AI-Powered Recruitment Intelligence Platform*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

*Revolutionize your hiring process with cutting-edge AI technology*

[Features](#-key-features) • [Tech Stack](#-technology-stack) • [Quick Start](#-quick-start) • [Documentation](#-api-documentation)

</div>

---

## 📋 Overview

**TalentPulse-AI** is an enterprise-grade, AI-powered recruitment platform that transforms traditional HR processes into intelligent, automated workflows. Built with modern technologies and advanced AI capabilities, it delivers unparalleled efficiency in talent acquisition, candidate evaluation, and job description optimization.

### 🎯 Why TalentPulse-AI?

- **🤖 Advanced AI Agents** - Multi-agent architecture powered by LangChain and Google Gemini
- **⚡ Lightning Fast** - Built on FastAPI for high-performance async operations
- **🔄 Intelligent Automation** - Automated resume parsing, JD generation, and candidate evaluation
- **📊 Data-Driven Insights** - ML-powered candidate scoring and matching algorithms
- **🔐 Enterprise Ready** - Scalable architecture with Docker support and environment-specific deployments
- **🌐 RESTful API** - Comprehensive API with auto-generated documentation

---

## ✨ Key Features

### 🎓 **Resume Intelligence**
- **Smart Resume Parsing** - Extract structured data from PDF, DOCX, and image formats using OCR
- **AI-Powered Analysis** - Deep candidate evaluation with skill matching and experience assessment
- **Automated Scoring** - ML-based candidate ranking and compatibility scoring
- **Multi-Format Support** - Handle various resume formats with intelligent text extraction

### 📝 **Job Description Management**
- **AI JD Generation** - Create compelling job descriptions from minimal input
- **Smart Enhancement** - Optimize existing JDs with AI-powered suggestions
- **Title Recommendations** - Get intelligent job title suggestions based on requirements
- **Automated Tagging** - Categorize and tag jobs automatically for better organization

### 💬 **Intelligent Chatbot**
- **Conversational AI** - Natural language interaction for HR queries
- **Context-Aware Responses** - Understand and respond to complex recruitment questions
- **24/7 Availability** - Always-on assistant for candidates and recruiters

### 📊 **Evaluation & Feedback**
- **Automated Assessments** - AI-driven candidate evaluation with detailed feedback
- **Custom Question Generation** - Create role-specific interview questions automatically
- **Performance Analytics** - Track and analyze recruitment metrics

---

## 🛠️ Technology Stack

### **Backend Framework**
- **[FastAPI](https://fastapi.tiangolo.com/)** `v0.116+` - Modern, high-performance Python web framework
- **[Uvicorn](https://www.uvicorn.org/)** `v0.35+` - Lightning-fast ASGI server
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** `v2.11+` - Data validation using Python type hints

### **AI & Machine Learning**
- **[LangChain](https://www.langchain.com/)** `v0.3.27` - Advanced LLM orchestration framework
- **[LangGraph](https://github.com/langchain-ai/langgraph)** `v0.6.6` - Multi-agent workflow orchestration
- **[Google Generative AI](https://ai.google.dev/)** `v0.8.5` - Google Gemini integration
- **[OpenAI](https://openai.com/)** `v1.101+` - GPT model integration
- **[FastEmbed](https://github.com/qdrant/fastembed)** - Fast, lightweight embedding generation
- **[scikit-learn](https://scikit-learn.org/)** - Machine learning utilities and algorithms

### **Document Processing**
- **[PyPDF2](https://pypdf2.readthedocs.io/)** `v3.0+` - PDF parsing and extraction
- **[pdf2image](https://github.com/Belval/pdf2image)** `v1.17+` - PDF to image conversion
- **[python-docx](https://python-docx.readthedocs.io/)** `v1.2+` - Microsoft Word document processing
- **[pytesseract](https://github.com/madmaze/pytesseract)** `v0.3+` - OCR for image-based text extraction
- **[Pillow](https://pillow.readthedocs.io/)** `v11.3+` - Advanced image processing

### **Database & Storage**
- **[SQLAlchemy](https://www.sqlalchemy.org/)** `v2.0+` - SQL toolkit and ORM
- **[sqlite-utils](https://sqlite-utils.datasette.io/)** - SQLite database utilities
- **[sqlite-fts4](https://www.sqlite.org/fts3.html)** - Full-text search capabilities

### **Development & Testing**
- **[pytest](https://pytest.org/)** `v8.4+` - Comprehensive testing framework
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment variable management
- **[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** - Settings management

### **Infrastructure**
- **[Docker](https://www.docker.com/)** - Containerization for consistent deployments
- **Multi-Environment Support** - Separate configurations for dev, staging, and production
- **[AWS CodeBuild](https://aws.amazon.com/codebuild/)** - CI/CD pipeline integration

### **Utilities & Tools**
- **[HTTPX](https://www.python-httpx.org/)** - Modern HTTP client
- **[Requests](https://requests.readthedocs.io/)** - HTTP library for API integrations
- **[python-dateutil](https://dateutil.readthedocs.io/)** - Powerful date/time handling
- **[tiktoken](https://github.com/openai/tiktoken)** - Token counting for LLM operations
- **[tenacity](https://tenacity.readthedocs.io/)** - Retry logic and resilience

---

## 🏗️ Architecture

```
TalentPulse-AI/
│
├── 🤖 agents/                    # AI Agent Layer
│   ├── resume_extractor.py      # Resume parsing & data extraction
│   ├── resume_analyze.py        # Candidate evaluation & scoring
│   ├── jd_genrator.py           # Job description generation
│   ├── jd_enhance.py            # JD optimization & enhancement
│   ├── jd_regenrate.py          # JD refinement engine
│   ├── jd_title_suggestion.py   # Smart job title recommendations
│   ├── job_taging.py            # Automated job categorization
│   ├── ai_question_generate.py  # Interview question generation
│   ├── ai_prompt_question.py    # Dynamic prompt engineering
│   ├── evaluation_agent.py      # Candidate assessment
│   ├── ai_feedback.py           # Automated feedback generation
│   └── ask_ai.py                # Conversational AI interface
│
├── 🌐 app/                       # Application Layer
│   ├── main.py                  # FastAPI application entry point
│   ├── models/                  # Pydantic data models & schemas
│   ├── routes/                  # API endpoint definitions
│   │   ├── resume_data.py       # Resume processing endpoints
│   │   ├── jd_operation.py      # Job description endpoints
│   │   ├── jd_refine.py         # JD refinement endpoints
│   │   ├── feedback_operation.py # Feedback endpoints
│   │   └── chatbot.py           # Chatbot endpoints
│   ├── services/                # Business logic layer
│   └── utils/                   # Helper functions & utilities
│
├── ⚙️ config/                    # Configuration Layer
│   ├── Settings.py              # Application settings
│   └── logging.py               # Logging configuration
│
├── 🧪 tests/                     # Testing Layer
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
│
├── 🐳 Dockerfile                 # Container configuration
├── 📦 requirements.txt           # Python dependencies
├── 🔧 buildspec.yml             # AWS CodeBuild specification
└── 📝 README.md                 # Documentation
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.8 or higher
- **pip** (Python package manager)
- **Docker** (optional, for containerized deployment)
- **Tesseract OCR** (for image-based resume processing)

### Installation

1️⃣ **Clone the repository**
```bash
git clone <repo-url>
cd TalentPulse-AI
```

2️⃣ **Create and activate virtual environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate on Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Activate on Windows CMD
.\.venv\Scripts\activate.bat

# Activate on Unix/MacOS
source venv/bin/activate
```

3️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

4️⃣ **Configure environment variables**
```bash
# Copy example environment file
cp env_example .env

# Edit .env with your configuration
# Add API keys for Google Gemini, OpenAI, etc.
```

5️⃣ **Run the application**
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Custom port
uvicorn app.main:app --reload --port 8080
```

🎉 **Your API is now running!**
- **Application**: http://127.0.0.1:8000
- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc

---

## 🐳 Docker Deployment

### Build for Specific Environment

```bash
# Development
docker build -t talentpulse-ai:dev --build-arg ENVIRONMENT=dev .

# Staging
docker build -t talentpulse-ai:stage --build-arg ENVIRONMENT=stage .

# Production
docker build -t talentpulse-ai:prod --build-arg ENVIRONMENT=prod .
```

### Run Container

```bash
# Development
docker run -p 8000:2001 --env-file .env.dev talentpulse-ai:dev

# Staging
docker run -p 8000:2001 --env-file .env.stage talentpulse-ai:stage

# Production
docker run -p 8000:2001 --env-file .env.prod talentpulse-ai:prod
```

---

## 📚 API Documentation

TalentPulse-AI provides comprehensive, auto-generated API documentation:

### **Swagger UI** (Interactive)
Access at: `http://localhost:8000/docs`
- Try out API endpoints directly from your browser
- View request/response schemas
- Test authentication and authorization

### **ReDoc** (Reference)
Access at: `http://localhost:8000/redoc`
- Clean, three-panel documentation
- Detailed endpoint descriptions
- Code samples and examples

### **Key API Endpoints**

#### Resume Processing
- `POST /api/v1/resume/upload` - Upload and parse resume
- `POST /api/v1/resume/analyze` - Analyze candidate profile
- `GET /api/v1/resume/{id}` - Retrieve parsed resume data

#### Job Description Management
- `POST /api/v1/jd/generate` - Generate new job description
- `POST /api/v1/jd/enhance` - Enhance existing JD
- `POST /api/v1/jd/refine` - Refine JD with AI suggestions
- `GET /api/v1/jd/title-suggestions` - Get job title recommendations

#### Feedback & Evaluation
- `POST /api/v1/feedback/generate` - Generate candidate feedback
- `POST /api/v1/evaluation/assess` - Evaluate candidate

#### Chatbot
- `POST /api/v1/chatbot/query` - Send query to AI chatbot

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_resume_parser.py -v

# Run tests matching pattern
pytest -k "test_jd" -v
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configurations:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=true

# AI Model Configuration
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
DATABASE_URL=sqlite:///./talentpulse.db

# Application Settings
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,docx,doc,png,jpg,jpeg
```

### Multi-Environment Setup

- `.env.dev` - Development configuration
- `.env.stage` - Staging configuration  
- `.env.prod` - Production configuration

---

## 🎯 Use Cases

### For Recruiters
- ✅ Automate resume screening and candidate shortlisting
- ✅ Generate professional job descriptions in seconds
- ✅ Get AI-powered candidate insights and recommendations
- ✅ Create customized interview questions automatically

### For HR Managers
- ✅ Streamline talent acquisition workflows
- ✅ Reduce time-to-hire with intelligent automation
- ✅ Improve candidate quality with AI-driven matching
- ✅ Scale recruitment operations efficiently

### For Organizations
- ✅ Build a modern, AI-powered recruitment infrastructure
- ✅ Integrate with existing HR systems via REST API
- ✅ Ensure data privacy and security with on-premise deployment
- ✅ Customize AI models for specific industry needs

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---
`
## 🌟 Support

For questions, issues, or feature requests:
- 📧 Email: support@talentpulse.ai
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/talentpulse-ai/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/talentpulse-ai/discussions)

---

<div align="center">

**Built with ❤️ using cutting-edge AI technology**

*Transform your recruitment process today with TalentPulse-AI*

[⬆ Back to Top](#-talentpulse-ai)

</div>
