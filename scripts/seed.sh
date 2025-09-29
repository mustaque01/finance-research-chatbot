#!/bin/bash

# Seed database with initial data
# Run this after the application is up and running

set -e

echo "🌱 Seeding Finance Research Chatbot database..."

# Wait for backend to be ready
echo "⏳ Waiting for backend service..."
until curl -f http://localhost:3001/health 2>/dev/null; do
    echo "Waiting for backend..."
    sleep 2
done

echo "✅ Backend is ready!"

# Create a demo user
echo "👤 Creating demo user..."
curl -X POST http://localhost:3001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@financechatbot.com",
    "password": "demo123456",
    "firstName": "Demo",
    "lastName": "User"
  }' || echo "Demo user might already exist"

echo "🎉 Database seeding complete!"
echo ""
echo "Demo credentials:"
echo "  Email: demo@financechatbot.com"
echo "  Password: demo123456"