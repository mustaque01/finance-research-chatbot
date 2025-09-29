# Finance Research Chatbot - Windows Setup Script
# PowerShell script to set up the development environment on Windows

param(
    [switch]$SkipBuild,
    [switch]$DevMode,
    [string]$Environment = "development"
)

Write-Host "🚀 Setting up Finance Research Chatbot on Windows..." -ForegroundColor Green

# Check if Docker Desktop is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file. Please update it with your API keys." -ForegroundColor Green
    Write-Host "⚠️  Required API keys:" -ForegroundColor Yellow
    Write-Host "   - OPENAI_API_KEY (required)" -ForegroundColor Yellow
    Write-Host "   - TAVILY_API_KEY (required for web search)" -ForegroundColor Yellow
    Write-Host "   - ALPHA_VANTAGE_API_KEY (recommended for financial data)" -ForegroundColor Yellow
    
    # Pause to let user update the .env file
    Read-Host "Press Enter after updating your .env file with API keys"
} else {
    Write-Host "✅ .env file already exists." -ForegroundColor Green
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
$directories = @(
    "backend\src\auth\guards",
    "backend\src\chat",
    "backend\src\threads",
    "backend\src\memory",
    "backend\src\agent",
    "backend\src\prisma",
    "backend\prisma\migrations",
    "frontend\src\app\login",
    "frontend\src\app\register",
    "frontend\src\app\chat",
    "frontend\src\components",
    "frontend\src\lib\context",
    "frontend\src\types",
    "frontend\public",
    "agents\app\agents",
    "agents\app\tools",
    "agents\app\memory",
    "agents\app\utils",
    "agents\tests"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories created." -ForegroundColor Green

# Start core services first
Write-Host "🔧 Starting core services (PostgreSQL, Redis)..." -ForegroundColor Yellow
docker-compose up -d postgres redis

# Wait for database to be ready
Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Build and start services
if (-not $SkipBuild) {
    Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
    docker-compose build
}

Write-Host "🚀 Starting all services..." -ForegroundColor Yellow
if ($DevMode) {
    # Start in development mode with live reload
    docker-compose -f docker-compose.yml up -d
} else {
    docker-compose up -d
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Run database migrations
Write-Host "📊 Running database migrations..." -ForegroundColor Yellow
docker-compose exec -T backend npm run prisma:migrate:deploy
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Migration command failed, but this is expected on first run." -ForegroundColor Yellow
}

# Seed database
Write-Host "🌱 Seeding database..." -ForegroundColor Yellow
docker-compose exec -T backend npm run seed
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Seeding command failed, but this is expected on first run." -ForegroundColor Yellow
}

# Display service URLs
Write-Host ""
Write-Host "🎉 Setup complete! Services are starting up:" -ForegroundColor Green
Write-Host "  - Frontend:        http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - Backend API:     http://localhost:3001" -ForegroundColor Cyan
Write-Host "  - Agent Service:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - pgAdmin:         http://localhost:5050" -ForegroundColor Cyan
Write-Host ""
Write-Host "📧 Demo credentials:" -ForegroundColor Yellow
Write-Host "  Email:    demo@financechatbot.com" -ForegroundColor White
Write-Host "  Password: demo123456" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:         docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop services:     docker-compose down" -ForegroundColor White
Write-Host "  Restart services:  docker-compose restart" -ForegroundColor White
Write-Host "  View status:       docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Important: Make sure to update your .env file with actual API keys!" -ForegroundColor Red