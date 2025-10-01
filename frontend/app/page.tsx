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
          py: { xs: 10, md: 16 },
          background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%)',
          borderRadius: 4,
          color: 'white',
          mb: 12,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 30% 20%, rgba(255,255,255,0.1) 0%, transparent 50%)',
          },
        }}
      >
        <Typography 
          variant="h1" 
          component="h1" 
          gutterBottom 
          sx={{ 
            fontWeight: 800,
            fontSize: { xs: '2.5rem', md: '3.5rem', lg: '4rem' },
            background: 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            color: 'transparent',
            mb: 3,
            position: 'relative',
            zIndex: 1,
          }}
        >
          Finance Research AI
        </Typography>
        <Typography 
          variant="h4" 
          component="h2" 
          gutterBottom 
          sx={{ 
            mb: 6, 
            opacity: 0.95,
            fontWeight: 400,
            fontSize: { xs: '1.25rem', md: '1.5rem' },
            maxWidth: '800px',
            mx: 'auto',
            lineHeight: 1.4,
            position: 'relative',
            zIndex: 1,
          }}
        >
          Transform your investment decisions with AI-powered research that analyzes market data, 
          news, and financial reports in real-time
        </Typography>
        <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', flexWrap: 'wrap', mt: 2 }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleGetStarted}
            sx={{
              bgcolor: 'rgba(255, 255, 255, 0.9)',
              color: 'primary.main',
              px: 4,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 500,
              borderRadius: 2,
              textTransform: 'none',
              boxShadow: '0 4px 12px rgba(255, 255, 255, 0.15)',
              '&:hover': {
                bgcolor: 'rgba(255, 255, 255, 0.95)',
                boxShadow: '0 6px 16px rgba(255, 255, 255, 0.2)',
                transform: 'translateY(-1px)',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          >
            Get Started Free
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={handleSignIn}
            sx={{
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: 3,
              textTransform: 'none',
              borderWidth: 2,
              borderColor: 'rgba(255, 255, 255, 0.3)',
              color: 'white',
              '&:hover': {
                borderColor: 'white',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                transform: 'translateY(-2px)',
              },
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          >
            Sign In
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ mb: 12, mt: 12 }}>
        <Typography 
          variant="h3" 
          component="h2" 
          textAlign="center" 
          gutterBottom 
          sx={{ 
            mb: 8,
            fontWeight: 700,
            background: 'linear-gradient(135deg, #2563eb 0%, #10b981 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            color: 'transparent',
          }}
        >
          Why Choose Our AI Research Platform
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={6} key={index}>
              <Card
                elevation={0}
                sx={{
                  height: '100%',
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: 3,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
                  },
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Box 
                      sx={{ 
                        color: 'white',
                        mr: 3,
                        p: 1.5,
                        background: 'linear-gradient(135deg, #2563eb 0%, #10b981 100%)',
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Typography 
                      variant="h5" 
                      component="h3" 
                      sx={{ 
                        fontWeight: 700,
                        color: 'white',
                        fontSize: '1.4rem',
                      }}
                    >
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: 'rgba(255, 255, 255, 0.8)',
                      fontSize: '1rem',
                      lineHeight: 1.6,
                    }}
                  >
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
        elevation={0}
        sx={{
          p: 6,
          textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: 4,
          mb: 12,
        }}
      >
        <Typography 
          variant="h4" 
          component="h2" 
          gutterBottom
          sx={{
            fontWeight: 700,
            mb: 3,
            background: 'linear-gradient(135deg, #2563eb 0%, #10b981 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            color: 'transparent',
          }}
        >
          Experience AI-Powered Research
        </Typography>
        <Paper
          elevation={0}
          sx={{
            p: 3,
            mb: 3,
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 2,
            maxWidth: '600px',
            mx: 'auto',
          }}
        >
          <Typography 
            variant="h6" 
            sx={{ 
              color: 'white',
              fontStyle: 'italic',
              fontWeight: 400,
            }}
          >
            "Is HDFC Bank undervalued compared to its peers in the last 2 quarters?"
          </Typography>
        </Paper>
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)',
            maxWidth: '700px',
            mx: 'auto',
            lineHeight: 1.6,
          }}
        >
          Our AI will research across multiple sources, analyze financial data, and provide a comprehensive answer with citations and real-time insights.
        </Typography>
      </Paper>

      {/* CTA Section */}
      <Box
        sx={{
          textAlign: 'center',
          py: 8,
          mb: 6,
          background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%)',
          borderRadius: 4,
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Typography 
          variant="h3" 
          component="h2" 
          gutterBottom
          sx={{
            fontWeight: 700,
            mb: 2,
            color: 'white',
          }}
        >
          Ready to Transform Your Research?
        </Typography>
        <Typography 
          variant="h6" 
          gutterBottom 
          sx={{ 
            mb: 4,
            color: 'rgba(255, 255, 255, 0.8)',
            maxWidth: '600px',
            mx: 'auto',
            fontWeight: 400,
          }}
        >
          Join thousands of investors and analysts using our AI-powered research platform.
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={handleGetStarted}
          sx={{ 
            px: 5, 
            py: 1.5,
            fontSize: '1.1rem',
            fontWeight: 500,
            borderRadius: 2,
            textTransform: 'none',
            boxShadow: '0 4px 12px rgba(37, 99, 235, 0.2)',
            '&:hover': {
              boxShadow: '0 6px 16px rgba(37, 99, 235, 0.25)',
              transform: 'translateY(-1px)',
            },
            transition: 'all 0.2s ease-in-out',
          }}
        >
          Start Your Free Trial
        </Button>
      </Box>
    </Container>
  );
}