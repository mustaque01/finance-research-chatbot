'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  List,
  ListItem,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import { Send, Logout } from '@mui/icons-material';
import { useAuth } from '@/lib/context/AuthContext';
import { chatAPI, threadsAPI } from '@/lib/api';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  
  const { user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push('/login');
    } else {
      // Create a new thread when user enters chat
      initializeThread();
    }
  }, [user, router]);

  const initializeThread = async () => {
    try {
      const response = await threadsAPI.create({ title: 'New Chat Session' });
      setThreadId(response.data.id);
    } catch (error) {
      console.error('Failed to create thread:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !threadId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Make actual API call to chat service
      const response = await chatAPI.sendMessage({
        message: input,
        threadId: threadId,
        metadata: {}
      });

      const botMessage: Message = {
        id: response.data.assistantMessage?.id || (Date.now() + 1).toString(),
        content: response.data.assistantMessage?.content || 'Sorry, I could not process your request.',
        isUser: false,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      
      // Show error message to user
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Sorry, there was an error processing your request: ${error.response?.data?.message || error.message || 'Unknown error'}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (!user) {
    return <CircularProgress />;
  }

  return (
    <>
      <AppBar 
        position="static" 
        elevation={0}
        sx={{
          background: 'linear-gradient(135deg, #2563eb 0%, #10b981 100%)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Toolbar>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              flexGrow: 1,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
            }}
          >
            Finance Research AI
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              mr: 3,
              color: 'rgba(255, 255, 255, 0.9)',
              fontWeight: 500,
            }}
          >
            Welcome, {user.name}
          </Typography>
          <IconButton 
            color="inherit" 
            onClick={handleLogout}
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            <Logout />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container 
        maxWidth="md" 
        sx={{ 
          mt: 3, 
          height: 'calc(100vh - 120px)', 
          display: 'flex', 
          flexDirection: 'column',
          pt: 3,
        }}
      >
        <Paper 
          elevation={0} 
          sx={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }}
        >
          {/* Messages */}
          <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
            {messages.length === 0 ? (
              <Box sx={{ textAlign: 'center', mt: 8 }}>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.8)',
                    mb: 2,
                    fontWeight: 600,
                  }}
                >
                  Start Your Financial Research
                </Typography>
                <Typography 
                  variant="body1" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.6)',
                    maxWidth: '400px',
                    mx: 'auto',
                    lineHeight: 1.6,
                  }}
                >
                  Ask about market trends, company analysis, or any financial research topic!
                </Typography>
              </Box>
            ) : (
              <List>
                {messages.map((message) => (
                  <ListItem
                    key={message.id}
                    sx={{
                      flexDirection: 'column',
                      alignItems: message.isUser ? 'flex-end' : 'flex-start',
                      mb: 1,
                    }}
                  >
                    <Paper
                      elevation={0}
                      sx={{
                        p: 3,
                        maxWidth: '75%',
                        background: message.isUser 
                          ? 'linear-gradient(135deg, #2563eb 0%, #10b981 100%)'
                          : 'rgba(255, 255, 255, 0.08)',
                        color: 'white',
                        borderRadius: 3,
                        border: message.isUser 
                          ? 'none'
                          : '1px solid rgba(255, 255, 255, 0.1)',
                        backdropFilter: message.isUser ? 'none' : 'blur(10px)',
                      }}
                    >
                      <Typography 
                        variant="body1"
                        sx={{
                          lineHeight: 1.6,
                          fontSize: '0.95rem',
                        }}
                      >
                        {message.content}
                      </Typography>
                    </Paper>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        mt: 1,
                        color: 'rgba(255, 255, 255, 0.5)',
                        fontSize: '0.75rem',
                      }}
                    >
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
            {loading && (
              <Box display="flex" justifyContent="center" alignItems="center" sx={{ mt: 3 }}>
                <CircularProgress 
                  size={28} 
                  sx={{ 
                    color: '#10b981',
                    mr: 2,
                  }} 
                />
                <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  AI is thinking...
                </Typography>
              </Box>
            )}
          </Box>

          {/* Input */}
          <Box sx={{ p: 3, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <Box display="flex" gap={2}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Ask about financial research, market trends, company analysis..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                disabled={loading}
                multiline
                maxRows={4}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: 2,
                    '& fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#10b981',
                    },
                  },
                  '& .MuiInputBase-input': {
                    color: 'white',
                  },
                  '& .MuiInputBase-input::placeholder': {
                    color: 'rgba(255, 255, 255, 0.5)',
                    opacity: 1,
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleSend}
                disabled={loading || !input.trim()}
                sx={{ 
                  minWidth: 'auto', 
                  px: 3,
                  py: 1.5,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #2563eb 0%, #10b981 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1d4ed8 0%, #059669 100%)',
                    transform: 'translateY(-1px)',
                  },
                  '&:disabled': {
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'rgba(255, 255, 255, 0.3)',
                  },
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                }}
              >
                <Send />
              </Button>
            </Box>
          </Box>
        </Paper>
      </Container>
    </>
  );
}