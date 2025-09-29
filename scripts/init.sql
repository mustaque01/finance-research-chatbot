-- Initialize PostgreSQL database with extensions

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- For pgvector if using local vector storage

-- Create indexes for better performance
-- These will be created by Prisma migrations, but having them here as reference

-- Sample indexes that will be useful:
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_created_at ON messages(created_at);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_threads_user_id ON threads(user_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memories_user_id ON memories(user_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops);

-- Set timezone
SET timezone = 'UTC';