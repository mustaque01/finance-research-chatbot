import { IsString, IsUUID, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class SendMessageDto {
  @ApiProperty({
    example: 'Is HDFC Bank undervalued compared to its peers?',
    description: 'The message content/question to send',
  })
  @IsString()
  message: string;

  @ApiProperty({
    example: 'uuid-thread-id',
    description: 'The thread ID to send the message to',
  })
  @IsUUID()
  threadId: string;

  @ApiProperty({
    example: { searchDepth: 'deep', includeCharts: true },
    description: 'Optional metadata for the message',
    required: false,
  })
  @IsOptional()
  metadata?: Record<string, any>;
}

export class MessageResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty()
  threadId: string;

  @ApiProperty()
  role: 'USER' | 'ASSISTANT' | 'SYSTEM';

  @ApiProperty()
  content: string;

  @ApiProperty({ required: false })
  thinkingTrace?: any;

  @ApiProperty({ required: false })
  metadata?: Record<string, any>;

  @ApiProperty()
  createdAt: Date;

  @ApiProperty({ required: false })
  sources?: Array<{
    id: string;
    url: string;
    title?: string;
    snippet?: string;
    domain?: string;
  }>;
}

export class StreamingResponseDto {
  @ApiProperty()
  type: 'token' | 'thinking' | 'source' | 'complete' | 'error';

  @ApiProperty()
  content?: string;

  @ApiProperty({ required: false })
  messageId?: string;

  @ApiProperty({ required: false })
  data?: any;
}