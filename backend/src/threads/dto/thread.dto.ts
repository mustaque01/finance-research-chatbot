import { IsString, IsOptional, IsUUID } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateThreadDto {
  @ApiProperty({
    example: 'HDFC Bank Analysis',
    description: 'Title of the conversation thread',
  })
  @IsString()
  title: string;
}

export class UpdateThreadDto {
  @ApiProperty({
    example: 'Updated HDFC Bank Analysis',
    description: 'Updated title of the conversation thread',
    required: false,
  })
  @IsOptional()
  @IsString()
  title?: string;
}

export class ThreadResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty()
  title: string;

  @ApiProperty()
  userId: string;

  @ApiProperty()
  createdAt: Date;

  @ApiProperty()
  updatedAt: Date;

  @ApiProperty({ required: false })
  messageCount?: number;

  @ApiProperty({ required: false })
  lastMessage?: {
    id: string;
    content: string;
    role: string;
    createdAt: Date;
  };
}