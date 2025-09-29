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
  
  const { user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  const handleSend = async () => {
    if (!input.trim()) return;

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
      // TODO: Implement actual API call to chat service
      // For now, just simulate a response
      setTimeout(() => {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: `I received your message: "${userMessage.content}". The chat functionality is being set up and will connect to the backend API soon.`,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, botMessage]);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Chat error:', error);
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
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Finance Research Chat
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            Welcome, {user.name}
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <Logout />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
        <Paper elevation={3} sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Messages */}
          <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
            {messages.length === 0 ? (
              <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mt: 4 }}>
                Start a conversation by asking about financial research topics!
              </Typography>
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
                      elevation={1}
                      sx={{
                        p: 2,
                        maxWidth: '70%',
                        bgcolor: message.isUser ? 'primary.main' : 'grey.100',
                        color: message.isUser ? 'white' : 'text.primary',
                      }}
                    >
                      <Typography variant="body1">{message.content}</Typography>
                    </Paper>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
            {loading && (
              <Box display="flex" justifyContent="center" sx={{ mt: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
          </Box>

          {/* Input */}
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box display="flex" gap={1}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Ask about financial research..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                disabled={loading}
                multiline
                maxRows={3}
              />
              <Button
                variant="contained"
                onClick={handleSend}
                disabled={loading || !input.trim()}
                sx={{ minWidth: 'auto', px: 2 }}
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