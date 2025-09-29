import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import { Toaster } from 'react-hot-toast';

import { theme } from '@/lib/theme';
import { AuthProvider } from '@/lib/context/AuthContext';
import { SWRProvider } from '@/lib/context/SWRProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Finance Research Chatbot',
  description: 'AI-powered financial research assistant with deep analysis and cited sources',
  keywords: ['finance', 'research', 'AI', 'chatbot', 'investment', 'analysis'],
  authors: [{ name: 'Finance Research Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'Finance Research Chatbot',
    description: 'AI-powered financial research assistant',
    type: 'website',
    locale: 'en_US',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppRouterCacheProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <SWRProvider>
              <AuthProvider>
                {children}
                <Toaster
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: '#363636',
                      color: '#fff',
                    },
                  }}
                />
              </AuthProvider>
            </SWRProvider>
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}