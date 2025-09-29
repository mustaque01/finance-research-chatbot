import { Injectable, NotFoundException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateThreadDto, UpdateThreadDto } from './dto/thread.dto';

@Injectable()
export class ThreadsService {
  constructor(private prisma: PrismaService) {}

  async create(userId: string, createThreadDto: CreateThreadDto) {
    const thread = await this.prisma.thread.create({
      data: {
        userId,
        title: createThreadDto.title,
      },
      include: {
        _count: {
          select: {
            messages: true,
          },
        },
      },
    });

    return {
      ...thread,
      messageCount: thread._count.messages,
    };
  }

  async findAll(userId: string, page = 1, limit = 20) {
    const skip = (page - 1) * limit;

    const [threads, total] = await Promise.all([
      this.prisma.thread.findMany({
        where: { userId },
        include: {
          _count: {
            select: {
              messages: true,
            },
          },
          messages: {
            take: 1,
            orderBy: {
              createdAt: 'desc',
            },
            select: {
              id: true,
              content: true,
              role: true,
              createdAt: true,
            },
          },
        },
        orderBy: {
          updatedAt: 'desc',
        },
        skip,
        take: limit,
      }),
      this.prisma.thread.count({
        where: { userId },
      }),
    ]);

    return {
      threads: threads.map((thread) => ({
        ...thread,
        messageCount: thread._count.messages,
        lastMessage: thread.messages[0] || null,
        messages: undefined,
        _count: undefined,
      })),
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string, userId: string) {
    const thread = await this.prisma.thread.findFirst({
      where: {
        id,
        userId,
      },
      include: {
        messages: {
          include: {
            sources: true,
          },
          orderBy: {
            createdAt: 'asc',
          },
        },
        _count: {
          select: {
            messages: true,
          },
        },
      },
    });

    if (!thread) {
      throw new NotFoundException('Thread not found');
    }

    return {
      ...thread,
      messageCount: thread._count.messages,
      _count: undefined,
    };
  }

  async update(id: string, userId: string, updateThreadDto: UpdateThreadDto) {
    // Check if thread exists and belongs to user
    const existingThread = await this.prisma.thread.findFirst({
      where: {
        id,
        userId,
      },
    });

    if (!existingThread) {
      throw new NotFoundException('Thread not found');
    }

    const updatedThread = await this.prisma.thread.update({
      where: { id },
      data: updateThreadDto,
      include: {
        _count: {
          select: {
            messages: true,
          },
        },
      },
    });

    return {
      ...updatedThread,
      messageCount: updatedThread._count.messages,
      _count: undefined,
    };
  }

  async remove(id: string, userId: string) {
    // Check if thread exists and belongs to user
    const existingThread = await this.prisma.thread.findFirst({
      where: {
        id,
        userId,
      },
    });

    if (!existingThread) {
      throw new NotFoundException('Thread not found');
    }

    await this.prisma.thread.delete({
      where: { id },
    });

    return { message: 'Thread deleted successfully' };
  }

  async validateThreadOwnership(threadId: string, userId: string): Promise<boolean> {
    const thread = await this.prisma.thread.findFirst({
      where: {
        id: threadId,
        userId,
      },
    });

    return !!thread;
  }
}