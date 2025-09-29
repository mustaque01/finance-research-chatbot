import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create demo user
  const hashedPassword = await bcrypt.hash('demo123456', 12);
  
  const demoUser = await prisma.user.upsert({
    where: { email: 'demo@financechatbot.com' },
    update: {},
    create: {
      email: 'demo@financechatbot.com',
      password: hashedPassword,
      firstName: 'Demo',
      lastName: 'User',
    },
  });

  console.log('✅ Created demo user:', demoUser.email);

  // Create sample thread
  const sampleThread = await prisma.thread.upsert({
    where: { id: 'sample-thread-id' },
    update: {},
    create: {
      id: 'sample-thread-id',
      userId: demoUser.id,
      title: 'Getting Started with Finance Research',
    },
  });

  console.log('✅ Created sample thread:', sampleThread.title);

  // Create sample messages
  await prisma.message.createMany({
    data: [
      {
        threadId: sampleThread.id,
        role: 'USER',
        content: 'Hello! Can you help me analyze HDFC Bank?',
      },
      {
        threadId: sampleThread.id,
        role: 'ASSISTANT',
        content: 'Hello! I\'d be happy to help you analyze HDFC Bank. I can provide insights on their financial performance, compare them with peers, analyze their stock valuation, and more. What specific aspect would you like to explore?',
        metadata: JSON.stringify({ demo: true }),
      },
    ],
  });

  console.log('✅ Created sample messages');

  // Create sample memory entries
  await prisma.memory.createMany({
    data: [
      {
        userId: demoUser.id,
        threadId: sampleThread.id,
        content: 'User is interested in HDFC Bank analysis',
        type: 'CONVERSATION',
        metadata: JSON.stringify({
          topic: 'banking',
          entity: 'HDFC Bank',
        }),
      },
      {
        userId: demoUser.id,
        content: 'HDFC Bank is one of India\'s largest private sector banks',
        type: 'FACT',
        metadata: JSON.stringify({
          entity: 'HDFC Bank',
          category: 'banking',
        }),
      },
    ],
  });

  console.log('✅ Created sample memories');

  console.log('🎉 Seeding completed successfully!');
  console.log('📧 Demo user: demo@financechatbot.com');
  console.log('🔑 Password: demo123456');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });