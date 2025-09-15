# 🧠 Quiz AI - Intelligent Quiz Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000.svg)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Transform your documents into intelligent quizzes with AI-powered question generation

Quiz AI is a full-stack web application that automatically generates comprehensive quizzes from uploaded documents using advanced AI technology. Upload PDFs, Word documents, or text files, and get personalized quizzes with multiple question types, explanations, and detailed analytics.

## ✨ Features

### 🎯 **Smart Quiz Generation**
- **AI-Powered**: Uses Groq's LLaMA 3.3 70B model for intelligent question generation
- **Multiple Formats**: Supports PDF, DOCX, and TXT file uploads
- **Question Types**: Single choice and multiple choice questions with explanations
- **Multilingual**: Automatically detects and generates questions in the document's language

### 🎮 **Two Quiz Modes**
- **📚 Practice Mode**: Immediate feedback, unlimited time, explanations shown
- **⏱️ Exam Mode**: Timed quizzes, results shown only after completion, auto-submit

### 👤 **User Management**
- **Authentication**: Secure user registration and login system
- **Guest Access**: Create quizzes without registration (cannot save)
- **Quiz Library**: Save and access your quiz history
- **Progress Tracking**: Comprehensive results analysis

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Updates**: Live progress indicators and status updates
- **Interactive Interface**: Drag-and-drop uploads, question navigation
- **Visual Feedback**: Toast notifications and loading states

## 🏗️ Architecture

### **Frontend** (React + TypeScript)
```
Frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utilities and API client
│   ├── App.tsx        # Main application
│   └── main.tsx       # Entry point
├── public/            # Static assets
└── dist/              # Production build
```

### **Backend** (Flask + Python)
```
Backend/
├── ai_models/         # AI processing modules
│   ├── text_processor.py    # Document text extraction
│   └── question_generator.py # AI quiz generation
├── app.py             # Main Flask application
├── uploads/           # Temporary file storage
└── requirements.txt   # Python dependencies
```

### **Database** (MySQL)
```
Database/
└── database_setup.py  # Database schema and setup
```

### **Testing Suite**
```
tests/
├── all_tests.py       # Comprehensive test suite
├── test_database.py   # Database testing utilities
├── run_tests.py       # Test orchestrator
└── tests_requirements.txt
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **MySQL 8.0+**
- **Groq API Key** ([Get one here](https://console.groq.com))

### 1. Clone Repository
```bash
git clone <repository-url>
cd Quiz_AI
```

### 2. Backend Setup
```bash
cd Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration:
# MYSQL_HOST=localhost
# MYSQL_USER=root
# MYSQL_PASSWORD=your_password
# GROQ_API_KEY=your_groq_api_key
```

### 3. Database Setup
```bash
# Start MySQL service
sudo systemctl start mysql  # On Linux
# brew services start mysql  # On macOS

# Setup database
cd ../Database
python3 database_setup.py
```

### 4. Frontend Setup
```bash
cd ../Frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 5. Run Application
```bash
# Start backend server
cd ../Backend
python3 app.py

# Server runs on http://localhost:8000
# Frontend served from Backend/static (after build)
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/register
Content-Type: application/json

{
  "mail": "user@example.com",
  "password": "secure_password"
}
```

#### Login User
```http
POST /api/login
Content-Type: application/json

{
  "mail": "user@example.com",
  "password": "secure_password"
}
```

### Quiz Generation

#### Generate Quiz
```http
POST /api/generate-questions
Content-Type: multipart/form-data

file: [PDF/DOCX/TXT file]
numQuestions: 5
mode: "practice" | "exam"
duration: 30 (minutes, for exam mode)
userId: 123
quizTitle: "My Quiz"
```

#### Check Job Status
```http
GET /api/job-status/{job_id}
```

### Quiz Management

#### Get User Quizzes
```http
GET /api/quizzes/user/{user_id}
```

#### Get Specific Quiz
```http
GET /api/quizzes/{quiz_id}
```

## 🧪 Testing

### Run Complete Test Suite
```bash
cd tests

# Install test dependencies
pip install -r tests_requirements.txt

# Start your Flask server first
cd ../Backend && python3 app.py

# Run all tests (in another terminal)
cd ../tests && python3 run_tests.py
```

### Test Coverage
- **Health Tests** (3): API connectivity and performance
- **Authentication Tests** (6): User registration and login flows
- **Quiz Generation Tests** (4): File upload and quiz creation

## 🛠️ Development

### Project Structure
```
Quiz_AI/
├── Frontend/          # React TypeScript application
├── Backend/           # Flask Python API
├── Database/          # MySQL schema and setup
├── tests/             # Comprehensive test suite
├── Scripts/           # Development utilities
└── README.md          # This file
```

### Tech Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, ShadCN/UI
- **Backend**: Flask, MySQL, Groq API, PyPDF2, python-docx
- **State Management**: Zustand (React), Session/Local Storage
- **Database**: MySQL with JSON storage for quiz data
- **Testing**: Custom test framework with database isolation

### Environment Variables
```env
# Backend/.env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
GROQ_API_KEY=your_groq_api_key
```

## 🔧 Configuration

### Database Schema
- **users**: User authentication and profiles
- **quizzes**: Quiz metadata and JSON data storage

### File Upload Limits
- Maximum file size: 10MB
- Supported formats: PDF, DOCX, TXT
- Text extraction with error handling

### AI Configuration
- Model: LLaMA 3.3 70B Versatile
- Temperature: 0.7
- Max tokens: 4096
- Multilingual support

## 🚦 Deployment

### Production Checklist
- [ ] Set secure database passwords
- [ ] Configure HTTPS
- [ ] Set up proper logging
- [ ] Configure file upload limits
- [ ] Set up database backups
- [ ] Monitor API rate limits

### Docker Support (Optional)
```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim
WORKDIR /app
COPY Backend/ .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing powerful AI models
- **React** and **Flask** communities
- **ShadCN/UI** for beautiful components
- **Tailwind CSS** for styling framework

## 📞 Support

For support create an issue in this repository.

---

**Made with ❤️ by ilay**
