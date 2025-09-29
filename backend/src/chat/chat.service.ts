import { Injectable, NotFoundException, HttpException, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import { ThreadsService } from '../threads/threads.service';
import { SendMessageDto } from './dto/chat.dto';
import axios from 'axios';

export interface StreamingResponse {
  type: 'token' | 'thinking' | 'source' | 'complete' | 'error';
  content?: string;
  messageId?: string;
  data?: any;
}

@Injectable()
export class ChatService {
  private readonly agentServiceUrl: string;

  constructor(
    private prisma: PrismaService,
    private threadsService: ThreadsService,
    private configService: ConfigService,
  ) {
    this.agentServiceUrl = this.configService.get<string>('AGENT_SERVICE_URL', 'http://agents:8000');
  }

  async sendMessage(userId: string, sendMessageDto: SendMessageDto) {
    const { message, threadId, metadata } = sendMessageDto;

    // Validate thread ownership
    const isOwner = await this.threadsService.validateThreadOwnership(threadId, userId);
    if (!isOwner) {
      throw new NotFoundException('Thread not found or access denied');
    }

    // Save user message
    const userMessage = await this.prisma.message.create({
      data: {
        threadId,
        role: 'USER',
        content: message,
        metadata: JSON.stringify(metadata || {}),
      },
    });

    // Get conversation history for context
    const conversationHistory = await this.getConversationHistory(threadId);

    // Prepare request to agent service
    const agentRequest = {
      message,
      threadId,
      userId,
      conversationHistory,
      metadata,
    };

    try {
      // Call agent service
      const response = await axios.post(
        `${this.agentServiceUrl}/chat/process`,
        agentRequest,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 300000, // 5 minutes timeout
        }
      );

      const agentResponse = response.data;

      // Save assistant message
      const assistantMessage = await this.prisma.message.create({
        data: {
          threadId,
          role: 'ASSISTANT',
          content: agentResponse.content,
          thinkingTrace: agentResponse.thinkingTrace,
          metadata: JSON.stringify(agentResponse.metadata || {}),
          sources: {
            create: agentResponse.sources?.map((source: any) => ({
              url: source.url,
              title: source.title,
              snippet: source.snippet,
              domain: source.domain,
              metadata: JSON.stringify(source.metadata || {}),
            })) || [],
          },
        },
        include: {
          sources: true,
        },
      });

      // Update thread timestamp
      await this.prisma.thread.update({
        where: { id: threadId },
        data: { updatedAt: new Date() },
      });

      return {
        userMessage,
        assistantMessage,
      };

    } catch (error) {
      console.error('Agent service error:', error.message);
      
      // Save error message
      const errorMessage = await this.prisma.message.create({
        data: {
          threadId,
          role: 'ASSISTANT',
          content: 'I apologize, but I encountered an error while processing your request. Please try again.',
          metadata: JSON.stringify({
            error: true,
            errorMessage: error.message,
          }),
        },
      });

      throw new HttpException(
        'Failed to process message with agent service',
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  async *streamMessage(userId: string, sendMessageDto: SendMessageDto): AsyncGenerator<StreamingResponse> {
    const { message, threadId, metadata } = sendMessageDto;

    // Validate thread ownership
    const isOwner = await this.threadsService.validateThreadOwnership(threadId, userId);
    if (!isOwner) {
      throw new NotFoundException('Thread not found or access denied');
    }

    // Save user message
    const userMessage = await this.prisma.message.create({
      data: {
        threadId,
        role: 'USER',
        content: message,
        metadata: JSON.stringify(metadata || {}),
      },
    });

    yield {
      type: 'complete',
      messageId: userMessage.id,
      data: { userMessage },
    };

    // Get conversation history
    const conversationHistory = await this.getConversationHistory(threadId);

    const agentRequest = {
      message,
      threadId,
      userId,
      conversationHistory,
      metadata: { ...metadata, streaming: true },
    };

    try {
      // Stream from agent service
      const response = await axios.post(
        `${this.agentServiceUrl}/chat/stream`,
        agentRequest,
        {
          responseType: 'stream',
          timeout: 300000,
        }
      );

      let assistantContent = '';
      let thinkingTrace: any = null;
      let sources: any[] = [];
      let assistantMessageId: string | null = null;

      // Process streaming response using async iteration
      const stream = response.data;
      let buffer = '';
      
      for await (const chunk of stream) {
        buffer += chunk.toString();
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'token':
                  assistantContent += data.content;
                  yield {
                    type: 'token',
                    content: data.content,
                  };
                  break;
                  
                case 'thinking':
                  thinkingTrace = data.data;
                  yield {
                    type: 'thinking',
                    data: data.data,
                  };
                  break;
                  
                case 'source':
                  sources.push(data.data);
                  yield {
                    type: 'source',
                    data: data.data,
                  };
                  break;
                  
                case 'complete':
                  // Stream complete, save final message
                  break;
              }
            } catch (parseError) {
              console.error('Error parsing stream data:', parseError);
            }
          }
        }
      }

      // Save final assistant message
      const assistantMessage = await this.prisma.message.create({
        data: {
          threadId,
          role: 'ASSISTANT',
          content: assistantContent,
          thinkingTrace: JSON.stringify(thinkingTrace || {}),
          metadata: JSON.stringify({ streaming: true }),
          sources: {
            create: sources.map((source) => ({
              url: source.url,
              title: source.title,
              snippet: source.snippet,
              domain: source.domain,
              metadata: JSON.stringify(source.metadata || {}),
            })),
          },
        },
        include: {
          sources: true,
        },
      });

      // Update thread timestamp
      await this.prisma.thread.update({
        where: { id: threadId },
        data: { updatedAt: new Date() },
      });

      yield {
        type: 'complete',
        messageId: assistantMessage.id,
        data: { assistantMessage },
      };

    } catch (error) {
      console.error('Streaming error:', error.message);
      
      yield {
        type: 'error',
        content: 'I apologize, but I encountered an error while processing your request.',
        data: { error: error.message },
      };
    }
  }

  private async getConversationHistory(threadId: string, limit = 10) {
    const messages = await this.prisma.message.findMany({
      where: { threadId },
      orderBy: { createdAt: 'desc' },
      take: limit,
      include: {
        sources: true,
      },
    });

    return messages.reverse(); // Return in chronological order
  }

  async getThreadMessages(threadId: string, userId: string, page = 1, limit = 50) {
    // Validate thread ownership
    const isOwner = await this.threadsService.validateThreadOwnership(threadId, userId);
    if (!isOwner) {
      throw new NotFoundException('Thread not found or access denied');
    }

    const skip = (page - 1) * limit;

    const [messages, total] = await Promise.all([
      this.prisma.message.findMany({
        where: { threadId },
        include: {
          sources: true,
        },
        orderBy: { createdAt: 'asc' },
        skip,
        take: limit,
      }),
      this.prisma.message.count({
        where: { threadId },
      }),
    ]);

    return {
      messages,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    };
  }
}