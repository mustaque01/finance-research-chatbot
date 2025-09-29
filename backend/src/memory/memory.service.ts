import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import { createClient } from 'redis';

@Injectable()
export class MemoryService {
  private redisClient: any;

  constructor(
    private prisma: PrismaService,
    private configService: ConfigService,
  ) {
    this.initializeRedis();
  }

  private async initializeRedis() {
    const redisUrl = this.configService.get<string>('REDIS_URL');
    this.redisClient = createClient({
      url: redisUrl,
    });

    this.redisClient.on('error', (err) => {
      console.error('Redis client error:', err);
    });

    this.redisClient.on('connect', () => {
      console.log('✅ Redis connected successfully');
    });

    await this.redisClient.connect();
  }

  async storeShortTermMemory(key: string, data: any, ttl = 3600) {
    try {
      await this.redisClient.setEx(
        key,
        ttl,
        JSON.stringify(data)
      );
    } catch (error) {
      console.error('Error storing short-term memory:', error);
    }
  }

  async getShortTermMemory(key: string) {
    try {
      const data = await this.redisClient.get(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error retrieving short-term memory:', error);
      return null;
    }
  }

  async storeLongTermMemory(
    userId: string,
    content: string,
    type: 'CONVERSATION' | 'FACT' | 'INSIGHT' | 'DOCUMENT',
    threadId?: string,
    metadata?: any,
  ) {
    try {
      // Store in database
      const memory = await this.prisma.memory.create({
        data: {
          userId,
          threadId,
          content,
          type,
          metadata,
        },
      });

      return memory;
    } catch (error) {
      console.error('Error storing long-term memory:', error);
      throw error;
    }
  }

  async searchMemories(userId: string, query: string, limit = 10) {
    try {
      // Simple text search for now - could be enhanced with vector similarity
      const memories = await this.prisma.memory.findMany({
        where: {
          userId,
          content: {
            contains: query,
            mode: 'insensitive',
          },
        },
        orderBy: {
          createdAt: 'desc',
        },
        take: limit,
      });

      return memories;
    } catch (error) {
      console.error('Error searching memories:', error);
      return [];
    }
  }

  async getConversationMemory(threadId: string) {
    try {
      const memories = await this.prisma.memory.findMany({
        where: {
          threadId,
          type: 'CONVERSATION',
        },
        orderBy: {
          createdAt: 'asc',
        },
      });

      return memories;
    } catch (error) {
      console.error('Error retrieving conversation memory:', error);
      return [];
    }
  }

  async cleanupExpiredMemories() {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 30); // Delete memories older than 30 days

    try {
      const result = await this.prisma.memory.deleteMany({
        where: {
          createdAt: {
            lt: cutoffDate,
          },
          type: 'CONVERSATION', // Only cleanup conversation memories
        },
      });

      console.log(`Cleaned up ${result.count} expired memories`);
      return result;
    } catch (error) {
      console.error('Error cleaning up memories:', error);
    }
  }
}