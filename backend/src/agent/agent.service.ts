import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';

@Injectable()
export class AgentService {
  private readonly agentServiceUrl: string;

  constructor(private configService: ConfigService) {
    this.agentServiceUrl = this.configService.get<string>('AGENT_SERVICE_URL', 'http://agents:8000');
  }

  async healthCheck() {
    try {
      const response = await axios.get(`${this.agentServiceUrl}/health`);
      return {
        status: 'healthy',
        agentService: response.data,
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
      };
    }
  }

  async processQuery(data: {
    message: string;
    threadId: string;
    userId: string;
    conversationHistory?: any[];
    metadata?: any;
  }) {
    try {
      const response = await axios.post(
        `${this.agentServiceUrl}/chat/process`,
        data,
        {
          timeout: 300000, // 5 minutes
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Agent service error:', error.message);
      throw new HttpException(
        'Failed to process query with agent service',
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  async streamQuery(data: {
    message: string;
    threadId: string;
    userId: string;
    conversationHistory?: any[];
    metadata?: any;
  }) {
    try {
      const response = await axios.post(
        `${this.agentServiceUrl}/chat/stream`,
        data,
        {
          responseType: 'stream',
          timeout: 300000,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Agent streaming error:', error.message);
      throw new HttpException(
        'Failed to stream query with agent service',
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  async getCapabilities() {
    try {
      const response = await axios.get(`${this.agentServiceUrl}/capabilities`);
      return response.data;
    } catch (error) {
      console.error('Error getting agent capabilities:', error.message);
      return {
        error: 'Failed to retrieve agent capabilities',
      };
    }
  }
}