# E2E Test Script for Finance Research Chatbot
# Tests the complete flow from frontend to backend to agent service

param(
    [string]$Environment = "development",
    [switch]$Verbose
)

Write-Host "🧪 Running E2E tests for Finance Research Chatbot..." -ForegroundColor Green

$apiUrl = "http://localhost:3001/api/v1"
$frontendUrl = "http://localhost:3000"
$agentUrl = "http://localhost:8000"

# Test functions
function Test-ServiceHealth {
    param([string]$url, [string]$serviceName)
    
    try {
        $response = Invoke-RestMethod -Uri "$url/health" -Method Get -TimeoutSec 10
        if ($response.status -eq "healthy" -or $response.status -eq "ok") {
            Write-Host "✅ $serviceName is healthy" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $serviceName is unhealthy: $($response.status)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ $serviceName is not responding: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-UserRegistration {
    $testEmail = "test-$(Get-Random)@example.com"
    $testPassword = "testpassword123"
    
    try {
        $body = @{
            email = $testEmail
            password = $testPassword
            firstName = "Test"
            lastName = "User"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$apiUrl/auth/register" -Method Post -Body $body -ContentType "application/json"
        
        if ($response.accessToken) {
            Write-Host "✅ User registration successful" -ForegroundColor Green
            return @{ success = $true; token = $response.accessToken; email = $testEmail; password = $testPassword }
        } else {
            Write-Host "❌ User registration failed: No access token returned" -ForegroundColor Red
            return @{ success = $false }
        }
    } catch {
        Write-Host "❌ User registration failed: $($_.Exception.Message)" -ForegroundColor Red
        return @{ success = $false }
    }
}

function Test-UserLogin {
    param([string]$email, [string]$password)
    
    try {
        $body = @{
            email = $email
            password = $password
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method Post -Body $body -ContentType "application/json"
        
        if ($response.accessToken) {
            Write-Host "✅ User login successful" -ForegroundColor Green
            return @{ success = $true; token = $response.accessToken }
        } else {
            Write-Host "❌ User login failed: No access token returned" -ForegroundColor Red
            return @{ success = $false }
        }
    } catch {
        Write-Host "❌ User login failed: $($_.Exception.Message)" -ForegroundColor Red
        return @{ success = $false }
    }
}

function Test-ThreadCreation {
    param([string]$token)
    
    try {
        $headers = @{ Authorization = "Bearer $token" }
        $body = @{ title = "Test Thread - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$apiUrl/threads" -Method Post -Body $body -ContentType "application/json" -Headers $headers
        
        if ($response.id) {
            Write-Host "✅ Thread creation successful" -ForegroundColor Green
            return @{ success = $true; threadId = $response.id }
        } else {
            Write-Host "❌ Thread creation failed: No thread ID returned" -ForegroundColor Red
            return @{ success = $false }
        }
    } catch {
        Write-Host "❌ Thread creation failed: $($_.Exception.Message)" -ForegroundColor Red
        return @{ success = $false }
    }
}

function Test-ChatMessage {
    param([string]$token, [string]$threadId)
    
    try {
        $headers = @{ Authorization = "Bearer $token" }
        $body = @{
            message = "What is the current market cap of Apple Inc?"
            threadId = $threadId
            metadata = @{ test = $true }
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$apiUrl/chat/send" -Method Post -Body $body -ContentType "application/json" -Headers $headers -TimeoutSec 60
        
        if ($response.assistantMessage -and $response.assistantMessage.content) {
            Write-Host "✅ Chat message successful" -ForegroundColor Green
            if ($Verbose) {
                Write-Host "   Response: $($response.assistantMessage.content.Substring(0, [Math]::Min(100, $response.assistantMessage.content.Length)))..." -ForegroundColor Gray
            }
            return @{ success = $true; messageId = $response.assistantMessage.id }
        } else {
            Write-Host "❌ Chat message failed: No response content" -ForegroundColor Red
            return @{ success = $false }
        }
    } catch {
        Write-Host "❌ Chat message failed: $($_.Exception.Message)" -ForegroundColor Red
        return @{ success = $false }
    }
}

function Test-AgentCapabilities {
    try {
        $response = Invoke-RestMethod -Uri "$agentUrl/api/v1/capabilities" -Method Get -TimeoutSec 10
        
        if ($response.version) {
            Write-Host "✅ Agent capabilities check successful" -ForegroundColor Green
            if ($Verbose) {
                Write-Host "   Version: $($response.version)" -ForegroundColor Gray
                Write-Host "   LLM Providers: $($response.llm_providers -join ', ')" -ForegroundColor Gray
                Write-Host "   Features: $($response.features.Count)" -ForegroundColor Gray
            }
            return $true
        } else {
            Write-Host "❌ Agent capabilities check failed: No version returned" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Agent capabilities check failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Run tests
Write-Host "🔍 Testing service health..." -ForegroundColor Yellow
$backendHealthy = Test-ServiceHealth -url $apiUrl -serviceName "Backend"
$agentHealthy = Test-ServiceHealth -url $agentUrl -serviceName "Agent Service"

if (-not $backendHealthy -or -not $agentHealthy) {
    Write-Host "❌ Services are not healthy. Please check your setup." -ForegroundColor Red
    exit 1
}

Write-Host "👤 Testing user registration and login..." -ForegroundColor Yellow
$registrationResult = Test-UserRegistration
if (-not $registrationResult.success) {
    Write-Host "❌ Cannot proceed without successful user registration." -ForegroundColor Red
    exit 1
}

$loginResult = Test-UserLogin -email $registrationResult.email -password $registrationResult.password
if (-not $loginResult.success) {
    Write-Host "❌ Cannot proceed without successful user login." -ForegroundColor Red
    exit 1
}

Write-Host "💬 Testing thread creation..." -ForegroundColor Yellow
$threadResult = Test-ThreadCreation -token $loginResult.token
if (-not $threadResult.success) {
    Write-Host "❌ Cannot proceed without successful thread creation." -ForegroundColor Red
    exit 1
}

Write-Host "🤖 Testing agent capabilities..." -ForegroundColor Yellow
$agentCapabilitiesResult = Test-AgentCapabilities
if (-not $agentCapabilitiesResult) {
    Write-Host "⚠️  Agent capabilities test failed, but continuing..." -ForegroundColor Yellow
}

Write-Host "💬 Testing chat message (this may take up to 60 seconds)..." -ForegroundColor Yellow
$chatResult = Test-ChatMessage -token $loginResult.token -threadId $threadResult.threadId
if (-not $chatResult.success) {
    Write-Host "❌ Chat message test failed." -ForegroundColor Red
    exit 1
}

# Summary
Write-Host ""
Write-Host "🎉 All E2E tests completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Test Results Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Backend Health Check" -ForegroundColor Green
Write-Host "  ✅ Agent Service Health Check" -ForegroundColor Green
Write-Host "  ✅ User Registration" -ForegroundColor Green
Write-Host "  ✅ User Login" -ForegroundColor Green
Write-Host "  ✅ Thread Creation" -ForegroundColor Green
Write-Host "  ✅ Chat Message Processing" -ForegroundColor Green
if ($agentCapabilitiesResult) {
    Write-Host "  ✅ Agent Capabilities" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Agent Capabilities (non-critical)" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "✅ Your Finance Research Chatbot is working correctly!" -ForegroundColor Green