#!/bin/bash

# Finance Research Chatbot Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Finance Research Chatbot..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your API keys."
else
    echo "✅ .env file already exists."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/src/{auth,chat,threads,memory,agent,prisma}
mkdir -p backend/prisma/migrations
mkdir -p frontend/src/{app,components,lib,types}
mkdir -p frontend/public
mkdir -p agents/app/{agents,tools,memory,utils}
mkdir -p agents/tests

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

echo "📊 Setting up database..."
docker-compose up -d backend

# Wait for backend to be ready
sleep 10

echo "🔧 Running database migrations..."
docker-compose exec -T backend npm run prisma:migrate:deploy || echo "Migration will run when backend is ready"

echo "🌱 Seeding database..."
docker-compose exec -T backend npm run seed || echo "Seeding will run when backend is ready"

echo "🎉 Setup complete!"
echo ""
echo "Services starting up:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:3001"
echo "  - Agent Service: http://localhost:8000"
echo "  - pgAdmin: http://localhost:5050"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
echo "⚠️  Important: Update your .env file with actual API keys before using the application!"