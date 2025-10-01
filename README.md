# 🚀 Finance Research Chatbot

> **Transform your investment decisions with AI-powered research that analyzes market data, news, and financial reports in real-time**

A comprehensive AI-powered finance research assistant built with modern web technologies, featuring a sleek interface, secure authentication, and intelligent chat capabilities for financial analysis and research.

![Project Banner](https://img.shields.io/badge/Finance-Research%20AI-blue?style=for-the-badge&logo=chart-line)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 📸 Screenshots

### 🏠 Homepage
*Modern landing page with professional design and call-to-action*

<!-- Add your homepage screenshot here -->

### 🔐 Authentication
*Secure login and registration system*

<!-- Add your login/register screenshot here -->

### 💬 Chat Interface
*Intuitive chat interface with real-time messaging*

<!-- Add your chat interface screenshot here -->

### 📱 Responsive Design
*Mobile-friendly design that works across all devices*

<!-- Add your mobile responsive screenshot here -->

---

## ✨ Features

### 🎯 **Core Functionality**
- 🤖 **AI-Powered Conversations**: Intelligent chat interface for financial queries
- � **Real-time Analysis**: Live market data integration and analysis
- 🔍 **Research Assistant**: Deep financial research with comprehensive insights  
- 💬 **Interactive Chat**: Modern, responsive chat interface with typing indicators
- 📝 **Message History**: Persistent conversation threads and history
- 🧠 **Context Awareness**: Maintains conversation context across sessions

### �️ **Security & Authentication**
- 👥 **Multi-User Support**: Secure user registration and authentication
- 🔐 **JWT Authentication**: Industry-standard token-based security
- 🛡️ **Protected Routes**: Secure access to chat functionality
- 📱 **Session Management**: Persistent login sessions with automatic refresh

### 🎨 **Modern UI/UX**
- 🌟 **Professional Design**: Modern gradient-based design system
- 🎨 **Glass-morphism Effects**: Contemporary UI with backdrop blur effects
- 📱 **Responsive Layout**: Optimized for desktop, tablet, and mobile
- 🌙 **Dark Theme**: Eye-friendly dark interface
- ⚡ **Smooth Animations**: Polished hover effects and transitions
- 🎯 **Intuitive Navigation**: User-friendly interface design

---

## 🛠️ Technology Stack

### 🖥️ **Frontend**
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **UI Library**: Material-UI (MUI) v5 with custom theming
- **Styling**: CSS-in-JS with gradient design system
- **State Management**: React Context API and SWR for data fetching
- **Authentication**: JWT token-based auth with persistent sessions

### ⚙️ **Backend**
- **Framework**: NestJS with Express
- **Language**: TypeScript with decorators
- **Database**: SQLite with Prisma ORM
- **Authentication**: JWT with Passport.js strategies
- **API**: RESTful endpoints with OpenAPI documentation
- **Architecture**: Modular design with dependency injection

### 🗄️ **Database & Storage**
- **Primary Database**: SQLite for development (PostgreSQL for production)
- **ORM**: Prisma with type-safe database queries
- **Migrations**: Automated database schema management
- **Models**: User management, conversation threads, message history

### 🎨 **Design System**
- **Color Palette**: Blue (#2563eb) and Green (#10b981) gradients
- **Typography**: Inter font family with custom font weights
- **Components**: Custom Material-UI theme with glass-morphism effects
- **Responsive**: Mobile-first design approach
- **Animations**: Smooth CSS transitions and hover effects

### 🤖 **AI Agents System (Python)**
- **Framework**: FastAPI with uvicorn server
- **AI Orchestration**: LangGraph for multi-agent workflows
- **Language Models**: OpenAI GPT-4, Anthropic Claude integration
- **Agent Types**: Researcher, Analyzer, Synthesizer specialists
- **Tools Integration**: Web scraping, financial APIs, data processing
- **Memory Management**: Persistent context and conversation history
- **Research Capabilities**: Real-time market data analysis and insights

---

## 🏗️ Architecture Overview

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │    │                 │
│    Frontend     │◄──►│     Backend     │◄──►│   AI Agents     │◄──►│    Database     │
│   (Next.js)     │    │   (NestJS)      │    │   (Python)      │    │   (SQLite)      │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │    │                 │
│  Material-UI    │    │  JWT Auth +     │    │  LangGraph +    │    │  Prisma ORM     │
│  + Custom CSS   │    │  API Routes     │    │  Research AI    │    │  + Migrations   │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 **Data Flow**
1. **User Authentication**: Secure login/registration with JWT tokens
2. **Chat Interface**: Real-time messaging with persistent threads
3. **API Communication**: RESTful endpoints for all operations
4. **Database Operations**: Type-safe queries with Prisma ORM
5. **State Management**: Context-based state with SWR caching

---

## 🚀 Quick Start

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: Version 18.0 or higher ([Download here](https://nodejs.org/))
- **npm**: Usually comes with Node.js
- **Git**: For cloning the repository ([Download here](https://git-scm.com/))

### 🔧 Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/mustaque01/finance-research-chatbot.git
cd finance-research-chatbot
```

#### 2️⃣ Install Backend Dependencies

```bash
cd backend
npm install
```

#### 3️⃣ Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

#### 4️⃣ Install AI Agents Dependencies (Optional)

```bash
cd ../agents
pip install -r requirements.txt
```

#### 5️⃣ Environment Setup

Create environment files:

```bash
# Backend environment
cd ../backend
cp .env.example .env

# Frontend environment  
cd ../frontend
cp .env.local.example .env.local

# AI Agents environment (if using agents)
cd ../agents
cp .env.example .env
```

#### 6️⃣ Database Setup

```bash
cd ../backend

# Generate Prisma client
npm run prisma:generate

# Run database migrations
npm run prisma:migrate:dev

# (Optional) Seed initial data
npm run seed
```

### 🏃‍♂️ Running the Application

#### Option 1: Development Mode (Recommended)

**Terminal 1 - Backend Server:**
```bash
cd backend
npm run build
node dist/main.js
```

**Terminal 2 - Frontend Server:**
```bash
cd frontend  
npm run dev
```

**Terminal 3 - AI Agents Service (Optional):**
```bash
cd agents
python -m uvicorn main:app --reload --port 8000
```

#### Option 2: Production Build

```bash
# Build backend
cd backend && npm run build

# Build frontend
cd ../frontend && npm run build

# Start backend
cd ../backend && npm run start:prod

# Start frontend
cd ../frontend && npm start
```

### 🌐 Access the Application

Once all servers are running:

- **🖥️ Frontend Application**: <http://localhost:3002>
- **🔧 Backend API**: <http://localhost:3001>
- **🤖 AI Agents API**: <http://localhost:8000>
- **📚 Backend API Documentation**: <http://localhost:3001/api/docs>
- **📚 AI Agents Documentation**: <http://localhost:8000/docs>
- **💚 Health Check**: <http://localhost:3001/api/v1/health>

### 👤 Getting Started

1. **Visit** <http://localhost:3002>
2. **Click** "Get Started Free" to create an account
3. **Fill** the registration form with your details
4. **Login** with your credentials
5. **Start** chatting with the AI research assistant!

---

## 🤖 AI Agents System (Python)

The application includes a sophisticated AI agent system built with Python for advanced financial research capabilities.

### 🏗️ **Agent Architecture**

#### **Core Components**
```text
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Service                          │
│                     (Python FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Researcher  │  │  Analyzer   │  │    Synthesizer      │  │
│  │   Agent     │  │   Agent     │  │      Agent          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                   LangGraph Orchestration                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Web Search  │  │   Memory    │  │     Tools           │  │
│  │   Tools     │  │  Manager    │  │   Integration       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 🚀 **Running AI Agents**

#### **Prerequisites**
```bash
# Python 3.11 or higher
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

#### **Installation**
```bash
cd agents
pip install -r requirements.txt
```

#### **Environment Setup**
Create `agents/.env` file:
```env
# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Research Tools
TAVILY_API_KEY=your_tavily_search_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Service Configuration
AGENT_PORT=8000
LOG_LEVEL=INFO
```

#### **Start Agent Service**
```bash
cd agents
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 🧠 **Agent Capabilities**

#### **1. Research Agent**
- **Web Search**: Intelligent search across financial websites
- **Data Extraction**: Scrapes and processes financial content
- **Source Verification**: Validates and ranks information sources
- **Market Data**: Real-time stock prices, news, and analysis

#### **2. Analyzer Agent** 
- **Financial Analysis**: Technical and fundamental analysis
- **Trend Detection**: Market patterns and trend identification
- **Risk Assessment**: Portfolio and investment risk analysis
- **Comparative Analysis**: Company and sector comparisons

#### **3. Synthesizer Agent**
- **Report Generation**: Comprehensive research reports
- **Citation Management**: Proper source attribution
- **Insight Synthesis**: Combines multiple data sources
- **Recommendation Engine**: Investment insights and recommendations

### 🔧 **Agent Workflow**

```python
# Example: Research Workflow
async def research_workflow(query: str) -> Dict[str, Any]:
    """
    1. Query Analysis    → Understand research intent
    2. Research Planning → Create multi-step strategy  
    3. Web Search       → Gather information
    4. Content Analysis → Process and analyze data
    5. Synthesis        → Generate insights
    6. Report Creation  → Format final response
    """
    pass
```

### 📊 **Key Features**

- **🔄 Multi-Agent Coordination**: LangGraph orchestrates agent interactions
- **🧠 Memory Management**: Persistent context across conversations
- **🔍 Advanced Search**: Multiple search providers and APIs
- **📈 Real-time Data**: Live market data integration
- **📝 Cited Research**: All responses include source citations
- **⚡ Streaming Responses**: Real-time response generation
- **🔒 Secure API**: JWT authentication and rate limiting

### 🌐 **Agent API Endpoints**

```http
# Research endpoint
POST /research
{
  "query": "Analyze Apple's Q3 earnings",
  "thread_id": "uuid",
  "user_id": "uuid"
}

# Agent status
GET /status

# Available tools
GET /tools
```

### 🔧 **Development & Testing**

```bash
# Run agent tests
cd agents
pytest tests/

# Test specific agent
python -m pytest tests/test_researcher.py

# Run with coverage
pytest --cov=app tests/
```

---

## 📚 API Documentation

### 🔐 Authentication Endpoints

#### Register New User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com", 
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "token": "jwt_token_here"
}
```

#### User Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "token": "jwt_token_here"  
}
```

#### Get User Profile
```http
GET /api/v1/auth/profile
Authorization: Bearer jwt_token_here
```

### 💬 Chat & Threads API

#### Create New Thread
```http
POST /api/v1/threads
Authorization: Bearer jwt_token_here
Content-Type: application/json

{
  "title": "HDFC Bank Analysis"
}
```

#### Send Chat Message
```http
POST /api/v1/chat/send
Authorization: Bearer jwt_token_here
Content-Type: application/json

{
  "threadId": "thread_uuid",
  "message": "What is the current market cap of Apple Inc?",
  "metadata": {}
}
```

#### Get Thread Messages
```http
GET /api/v1/chat/threads/{threadId}/messages
Authorization: Bearer jwt_token_here
```

### 🏥 Health Check

#### System Health
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-01T20:30:00.000Z",
  "uptime": 3600,
  "database": "connected"
}
```

---

## 🔧 Development Guide

### 💻 Local Development Setup

For developers who want to contribute or customize the application:

#### Environment Setup

```bash
# Install dependencies
cd backend && npm install
cd ../frontend && npm install
```

#### Development Servers

```bash
# Terminal 1: Backend (with hot reload)
cd backend && npm run start:dev

# Terminal 2: Frontend (with hot reload)  
cd frontend && npm run dev
```

### 🗄️ Database Operations

#### Prisma Commands

```bash
cd backend

# Generate Prisma client after schema changes
npm run prisma:generate

# Create and apply new migration
npm run prisma:migrate:dev --name migration_name

# Reset database (⚠️ Deletes all data)
npm run prisma:reset

# Open Prisma Studio (Database GUI)
npm run prisma:studio
```

#### Database Schema

The application uses the following main models:

- **User**: Authentication and profile information
- **Thread**: Conversation threads/sessions
- **Message**: Individual chat messages
- **Memory**: Context and conversation history

### 🧪 Testing

```bash
# Backend unit tests
cd backend && npm run test

# Frontend component tests
cd frontend && npm run test

# End-to-end tests
npm run test:e2e

# Test coverage
npm run test:cov
```

### 🔍 Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

---

## ⚙️ Configuration

### 🔧 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JWT_SECRET` | JWT signing secret (32+ characters) | ✅ Yes | - |
| `DATABASE_URL` | SQLite database path | ✅ Yes | `./dev.db` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | ✅ Yes | `http://localhost:3001` |
| `NODE_ENV` | Environment mode | ❌ No | `development` |
| `PORT` | Backend server port | ❌ No | `3001` |

### 📝 Example Environment Files

**Backend (.env)**:
```env
# Database
DATABASE_URL="file:./dev.db"

# Authentication
JWT_SECRET="your-super-secure-jwt-secret-key-32-characters-minimum"

# Server
PORT=3001
NODE_ENV=development
```

**Frontend (.env.local)**:
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001

# Environment
NODE_ENV=development
```

---

## 🚀 Deployment

### 📦 Production Build

```bash
# Build backend
cd backend
npm run build

# Build frontend
cd ../frontend  
npm run build

# Start production servers
cd ../backend && npm run start:prod
cd ../frontend && npm start
```

### 🐳 Docker Deployment (Optional)

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 🌐 Environment-Specific Configurations

- **Development**: Hot reload, detailed logging, development database
- **Production**: Optimized builds, security headers, production database
- **Testing**: In-memory database, mocked external services

---

## 🔍 Troubleshooting

### ❗ Common Issues

#### 🚫 Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :3001

# Kill process (Windows)
taskkill /PID <process_id> /F

# Kill process (Mac/Linux)
sudo kill -9 <process_id>
```

#### 🗄️ Database Issues
```bash
# Reset database
cd backend
npm run prisma:reset

# Regenerate Prisma client
npm run prisma:generate

# Create new migration
npm run prisma:migrate:dev
```

#### 🔐 Authentication Problems
- Ensure JWT_SECRET is set and 32+ characters
- Check if tokens are properly included in requests
- Verify API endpoints are not cached

#### 🎨 UI/Styling Issues
- Clear browser cache and refresh
- Check if CSS is loading properly
- Verify Material-UI theme is applied

### 📊 Debugging Commands

```bash
# Check backend health
curl http://localhost:3001/api/v1/health

# View detailed logs
cd backend && npm run start:dev

# Test API endpoints
cd backend && npm run test

# Check database connection
cd backend && npm run prisma:studio
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 🛠️ Development Workflow

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes with proper tests
5. **Commit** with descriptive messages: `git commit -m 'Add amazing feature'`
6. **Push** to your branch: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request

### 📋 Contribution Guidelines

- **Code Style**: Follow existing TypeScript/JavaScript conventions
- **Tests**: Add tests for new features and bug fixes
- **Documentation**: Update README and code comments
- **Commits**: Use clear, descriptive commit messages
- **Issues**: Reference issues in your PR description

### 🧪 Before Submitting

```bash
# Run all tests
npm run test

# Check code formatting
npm run lint

# Verify build works
npm run build

# Test locally
npm run start:dev
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Community

### 📞 Getting Help

- **🐛 Bug Reports**: [Create an issue on GitHub](https://github.com/mustaque01/finance-research-chatbot/issues)
- **💡 Feature Requests**: [Submit enhancement ideas](https://github.com/mustaque01/finance-research-chatbot/issues)
- **📖 Documentation**: Check this README and code comments
- **🔧 Troubleshooting**: Review the troubleshooting section above

### 🌟 Acknowledgments

- **Next.js Team** for the excellent React framework
- **NestJS Team** for the powerful Node.js framework  
- **Material-UI Team** for the beautiful component library
- **Prisma Team** for the amazing database toolkit
- **Open Source Community** for inspiration and contributions

---

**Made with ❤️ by the Finance Research Team**

*Transform your investment decisions with AI-powered research!*