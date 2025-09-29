import {
  Controller,
  Post,
  Body,
  UseGuards,
  Request,
  Get,
  Param,
  Query,
  ParseIntPipe,
  Sse,
  MessageEvent,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
} from '@nestjs/swagger';
import { Observable } from 'rxjs';
import { ChatService } from './chat.service';
import { SendMessageDto, MessageResponseDto } from './dto/chat.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('chat')
@Controller('chat')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Post('send')
  @ApiOperation({ summary: 'Send a message and get response' })
  @ApiResponse({
    status: 201,
    description: 'Message sent and response generated',
    type: MessageResponseDto,
  })
  async sendMessage(@Request() req, @Body() sendMessageDto: SendMessageDto) {
    return this.chatService.sendMessage(req.user.id, sendMessageDto);
  }

  @Post('stream')
  @Sse()
  @ApiOperation({ summary: 'Send a message and stream the response' })
  async streamMessage(
    @Request() req,
    @Body() sendMessageDto: SendMessageDto,
  ): Promise<Observable<MessageEvent>> {
    return new Observable((observer) => {
      (async () => {
        try {
          const stream = this.chatService.streamMessage(req.user.id, sendMessageDto);
          
          for await (const chunk of stream) {
            observer.next({
              data: JSON.stringify(chunk),
            } as MessageEvent);
          }
          
          observer.complete();
        } catch (error) {
          observer.error(error);
        }
      })();
    });
  }

  @Get('threads/:threadId/messages')
  @ApiOperation({ summary: 'Get messages for a thread' })
  @ApiResponse({
    status: 200,
    description: 'Messages retrieved successfully',
    type: [MessageResponseDto],
  })
  async getThreadMessages(
    @Param('threadId') threadId: string,
    @Request() req,
    @Query('page', new ParseIntPipe({ optional: true })) page = 1,
    @Query('limit', new ParseIntPipe({ optional: true })) limit = 50,
  ) {
    return this.chatService.getThreadMessages(threadId, req.user.id, page, limit);
  }
}