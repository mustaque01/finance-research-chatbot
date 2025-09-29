'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Container, 
  Typography, 
  Button, 
  Box, 
  Card, 
  CardContent,
  Grid,
  Paper
} from '@mui/material';
import {
  TrendingUp,
  Search,
  Analytics,
  AutoAwesome
} from '@mui/icons-material';

import { useAuth } from '@/lib/context/AuthContext';

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/chat');
    }
  }, [user, loading, router]);

  const handleGetStarted = () => {
    router.push('/register');
  };

  const handleSignIn = () => {
    router.push('/login');
  };

  const features = [
    {
      icon: <Search sx={{ fontSize: 40 }} />,
      title: 'Intelligent Research',
      description: 'AI-powered web research across multiple financial sources with real-time data collection.',
    },
    {
      icon: <Analytics sx={{ fontSize: 40 }} />,
      title: 'Deep Analysis',
      description: 'Multi-agent analysis system that provides comprehensive insights with reasoning transparency.',
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      title: 'Market Intelligence',
      description: 'Real-time market data integration from multiple providers including Alpha Vantage and Yahoo Finance.',
    },
    {
      icon: <AutoAwesome sx={{ fontSize: 40 }} />,
      title: 'Cited Sources',
      description: 'Every response includes citations and sources, ensuring transparency and reliability.',
    },
  ];

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box
        sx={{
          textAlign: 'center',
          py: { xs: 8, md: 12 },
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: 3,
          color: 'white',
          mb: 8,
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Finance Research Chatbot
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 4, opacity: 0.9 }}>
          AI-powered financial research assistant with deep analysis and cited sources
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleGetStarted}
            sx={{
              bgcolor: 'white',
              color: 'primary.main',
              '&:hover': {
                bgcolor: 'grey.100',
              },
              px: 4,
              py: 1.5,
            }}
          >
            Get Started
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={handleSignIn}
            sx={{
              borderColor: 'white',
              color: 'white',
              '&:hover': {
                borderColor: 'white',
                bgcolor: 'rgba(255,255,255,0.1)',
              },
              px: 4,
              py: 1.5,
            }}
          >
            Sign In
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ mb: 8 }}>
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom sx={{ mb: 6 }}>
          Powerful Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={6} key={index}>
              <Card
                elevation={2}
                sx={{
                  height: '100%',
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    elevation: 4,
                  },
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ color: 'primary.main', mr: 2 }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h5" component="h3" fontWeight="bold">
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography variant="body1" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Demo Section */}
      <Paper
        elevation={3}
        sx={{
          p: 4,
          textAlign: 'center',
          bgcolor: 'grey.50',
          mb: 8,
        }}
      >
        <Typography variant="h4" component="h2" gutterBottom>
          Try a Sample Query
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
          "Is HDFC Bank undervalued compared to its peers in the last 2 quarters?"
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
          Our AI will research across multiple sources, analyze financial data, and provide a comprehensive answer with citations.
        </Typography>
      </Paper>

      {/* CTA Section */}
      <Box
        sx={{
          textAlign: 'center',
          py: 6,
          mb: 4,
        }}
      >
        <Typography variant="h4" component="h2" gutterBottom>
          Ready to Start Researching?
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
          Join thousands of investors and analysts using our AI-powered research platform.
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={handleGetStarted}
          sx={{ px: 4, py: 1.5 }}
        >
          Create Free Account
        </Button>
      </Box>
    </Container>
  );
}