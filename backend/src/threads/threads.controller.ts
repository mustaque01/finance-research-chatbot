import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  UseGuards,
  Request,
  Query,
  ParseIntPipe,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiQuery,
} from '@nestjs/swagger';
import { ThreadsService } from './threads.service';
import { CreateThreadDto, UpdateThreadDto, ThreadResponseDto } from './dto/thread.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('threads')
@Controller('threads')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class ThreadsController {
  constructor(private readonly threadsService: ThreadsService) {}

  @Post()
  @ApiOperation({ summary: 'Create a new conversation thread' })
  @ApiResponse({ 
    status: 201, 
    description: 'Thread created successfully',
    type: ThreadResponseDto 
  })
  async create(@Request() req, @Body() createThreadDto: CreateThreadDto) {
    return this.threadsService.create(req.user.id, createThreadDto);
  }

  @Get()
  @ApiOperation({ summary: 'Get all threads for the current user' })
  @ApiQuery({ name: 'page', required: false, type: Number, description: 'Page number' })
  @ApiQuery({ name: 'limit', required: false, type: Number, description: 'Items per page' })
  @ApiResponse({ 
    status: 200, 
    description: 'Threads retrieved successfully',
    type: [ThreadResponseDto] 
  })
  async findAll(
    @Request() req,
    @Query('page', new ParseIntPipe({ optional: true })) page = 1,
    @Query('limit', new ParseIntPipe({ optional: true })) limit = 20,
  ) {
    return this.threadsService.findAll(req.user.id, page, limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a specific thread with messages' })
  @ApiResponse({ 
    status: 200, 
    description: 'Thread retrieved successfully',
    type: ThreadResponseDto 
  })
  @ApiResponse({ status: 404, description: 'Thread not found' })
  async findOne(@Param('id') id: string, @Request() req) {
    return this.threadsService.findOne(id, req.user.id);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Update a thread' })
  @ApiResponse({ 
    status: 200, 
    description: 'Thread updated successfully',
    type: ThreadResponseDto 
  })
  @ApiResponse({ status: 404, description: 'Thread not found' })
  async update(
    @Param('id') id: string,
    @Request() req,
    @Body() updateThreadDto: UpdateThreadDto,
  ) {
    return this.threadsService.update(id, req.user.id, updateThreadDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a thread' })
  @ApiResponse({ status: 200, description: 'Thread deleted successfully' })
  @ApiResponse({ status: 404, description: 'Thread not found' })
  async remove(@Param('id') id: string, @Request() req) {
    return this.threadsService.remove(id, req.user.id);
  }
}