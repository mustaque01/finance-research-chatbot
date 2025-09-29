# Finance Research Chatbot

A comprehensive AI-powered finance research assistant that provides deep analysis with cited sources and reasoning transparency.

## Features

- 🤖 **AI-Powered Research**: Multi-agent system with specialized researchers, analyzers, and synthesizers
- 📊 **Financial Data Integration**: Real-time market data from multiple providers
- 🔍 **Web Research**: Intelligent web scraping and search across financial sources
- 💬 **Interactive Chat**: Real-time streaming responses with thinking traces
- 📝 **Cited Reports**: All responses include source citations and reasoning
- 🧠 **Memory System**: Maintains context across conversations
- 👥 **Multi-User**: Secure authentication with thread management

## Architecture

- **Frontend**: Next.js with TypeScript, Material-UI
- **Backend**: NestJS with WebSocket support
- **AI Agents**: Python with LangGraph workflow orchestration
- **Database**: PostgreSQL with Prisma ORM
- **Caching**: Redis for sessions and agent checkpoints
- **Memory**: Vector database for long-term knowledge retention

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd finance-research-chatbot
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your API keys:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Database credentials
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET=your_jwt_secret_32_chars_minimum
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec backend npm run prisma:migrate

# Seed initial data (optional)
docker-compose exec backend npm run seed
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **Agent Service**: http://localhost:8000
- **pgAdmin**: http://localhost:5050 (dev only)

## API Documentation

### Authentication

```bash
# Register user
POST /auth/register
{
  "email": "user@example.com",
  "password": "securepassword"
}

# Login
POST /auth/login
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Chat API

```bash
# Create new thread
POST /threads
{
  "title": "HDFC Bank Analysis"
}

# Send message (streaming response)
POST /chat/stream
{
  "threadId": "uuid",
  "message": "Is HDFC Bank undervalued vs peers?"
}
```

## Development

### Local Development Setup

```bash
# Install dependencies
cd backend && npm install
cd ../frontend && npm install
cd ../agents && pip install -r requirements.txt

# Start services individually
cd backend && npm run start:dev
cd frontend && npm run dev
cd agents && python main.py
```

### Database Operations

```bash
# Generate Prisma client
npm run prisma:generate

# Create migration
npm run prisma:migrate:dev

# Reset database
npm run prisma:reset

# View database
npm run prisma:studio
```

### Testing

```bash
# Backend tests
cd backend && npm run test

# Frontend tests
cd frontend && npm run test

# Agent tests
cd agents && pytest

# E2E tests
npm run test:e2e
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes |
| `TAVILY_API_KEY` | Tavily search API key | Yes |
| `ALPHA_VANTAGE_API_KEY` | Stock data API key | Recommended |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `JWT_SECRET` | JWT signing secret | Yes |

### Agent Configuration

The AI agent system uses LangGraph to orchestrate research workflows:

1. **Query Analysis**: Understands financial query intent
2. **Research Planning**: Creates multi-step research strategy
3. **Web Search**: Searches across multiple providers
4. **Content Extraction**: Scrapes and parses financial content
5. **Analysis**: Processes and analyzes collected data
6. **Synthesis**: Generates cited reports
7. **Memory Update**: Stores insights for future queries

## Deployment

### Production Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production settings
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configs

- **Development**: Full logging, hot reload, pgAdmin
- **Production**: Optimized builds, security headers, monitoring

## API Keys Setup

### Required Services

1. **OpenAI**: Get key from https://platform.openai.com/
2. **Tavily**: Register at https://tavily.com/
3. **Alpha Vantage**: Free tier at https://www.alphavantage.co/

### Optional Services

- **Anthropic Claude**: Alternative LLM
- **Pinecone**: Managed vector database
- **Financial Modeling Prep**: Enhanced financial data

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running
2. **API Rate Limits**: Check API key quotas
3. **Memory Issues**: Increase Docker memory allocation
4. **Port Conflicts**: Change ports in docker-compose.yml

### Logs

```bash
# View all service logs
docker-compose logs

# View specific service
docker-compose logs backend
docker-compose logs agents
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide