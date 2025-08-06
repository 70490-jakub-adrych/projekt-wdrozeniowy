# PowerShell Live Domain Testing Script for Windows
# This script helps you run comprehensive tests on your live domain

param(
    [string]$Action = "menu",
    [string]$AdminUser = "",
    [string]$AdminPass = "",
    [string]$TestEmail = "",
    [string]$Domain = "https://dev.betulait.usermd.net"
)

# Configuration
$DOMAIN_URL = $Domain
$PROJECT_PATH = Get-Location  # Current directory
$PYTHON_CMD = "python"  # or "python3" on some systems

Write-Host "==================================="
Write-Host "🚀 Live Domain Testing Setup (Windows)"
Write-Host "==================================="
Write-Host "Domain: $DOMAIN_URL"
Write-Host "Project Path: $PROJECT_PATH"
Write-Host ""

# Function to install Python dependencies
function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..."
    
    try {
        # Install testing dependencies
        & $PYTHON_CMD -m pip install selenium==4.15.0
        & $PYTHON_CMD -m pip install pytest==7.4.3
        & $PYTHON_CMD -m pip install pytest-django==4.7.0
        & $PYTHON_CMD -m pip install webdriver-manager==4.0.1
        & $PYTHON_CMD -m pip install pyotp==2.9.0
        & $PYTHON_CMD -m pip install Pillow
        & $PYTHON_CMD -m pip install qrcode
        
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error installing dependencies: $_" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to install Chrome and ChromeDriver
function Install-Chrome {
    Write-Host "📦 Installing Chrome and ChromeDriver..."
    
    # Check if Chrome is already installed
    $chromeInstalled = Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe"
    $chromeInstalled = $chromeInstalled -or (Test-Path "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    
    if (-not $chromeInstalled) {
        Write-Host "Chrome not found. Please install Google Chrome manually from:"
        Write-Host "https://www.google.com/chrome/" -ForegroundColor Yellow
        Write-Host "Then run this script again."
        return $false
    }
    else {
        Write-Host "✅ Chrome is already installed" -ForegroundColor Green
    }
    
    # Install ChromeDriver using webdriver-manager (Python will handle this)
    try {
        & $PYTHON_CMD -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
        Write-Host "✅ ChromeDriver installed/updated" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  ChromeDriver installation failed, but webdriver-manager will handle it during tests" -ForegroundColor Yellow
    }
    
    return $true
}

# Function to run comprehensive tests
function Run-Tests {
    Write-Host "🧪 Running Comprehensive Live Domain Tests..."
    
    # Get admin credentials if not provided
    if (-not $AdminUser) {
        $AdminUser = Read-Host "Admin Username"
    }
    if (-not $AdminPass) {
        $AdminPass = Read-Host "Admin Password" -AsSecureString
        $AdminPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($AdminPass))
    }
    if (-not $TestEmail) {
        $TestEmail = Read-Host "Test Email Address"
    }
    
    try {
        # Run the comprehensive test
        & $PYTHON_CMD manage.py comprehensive_live_test --username="$AdminUser" --password="$AdminPass" --domain="$DOMAIN_URL" --headless
        
        Write-Host ""
        Write-Host "🏁 Test execution completed!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Test execution failed: $_" -ForegroundColor Red
    }
}

# Function to run specific test categories
function Run-SpecificTests {
    Write-Host "🎯 Select specific test categories to run:"
    Write-Host "1. Authentication & Security Tests"
    Write-Host "2. 2FA System Tests"
    Write-Host "3. Organization Management Tests"
    Write-Host "4. Email System Tests"
    Write-Host "5. Mobile Responsiveness Tests"
    Write-Host "6. All Tests"
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-6)"
    
    switch ($choice) {
        1 {
            Write-Host "Running Authentication & Security Tests..."
            # Add specific test command here
        }
        2 {
            Write-Host "Running 2FA System Tests..."
            # Add specific test command here
        }
        3 {
            Write-Host "Running Organization Management Tests..."
            # Add specific test command here
        }
        4 {
            Write-Host "Running Email System Tests..."
            # Add specific test command here
        }
        5 {
            Write-Host "Running Mobile Responsiveness Tests..."
            # Add specific test command here
        }
        6 {
            Run-Tests
        }
        default {
            Write-Host "Invalid choice. Running all tests..."
            Run-Tests
        }
    }
}

# Function to cleanup test data
function Cleanup-TestData {
    Write-Host "🧹 Cleaning up test data..."
    
    # Get admin credentials
    $AdminUser = Read-Host "Admin Username"
    $AdminPass = Read-Host "Admin Password" -AsSecureString
    $AdminPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($AdminPass))
    
    try {
        & $PYTHON_CMD manage.py comprehensive_live_test --username="$AdminUser" --password="$AdminPass" --domain="$DOMAIN_URL" --cleanup-only --headless
        
        Write-Host "✅ Cleanup completed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Cleanup failed: $_" -ForegroundColor Red
    }
}

# Function to monitor system resources
function Monitor-Resources {
    Write-Host "📊 System Resource Monitoring During Tests..."
    Write-Host "Press Ctrl+C to stop monitoring"
    
    while ($true) {
        Clear-Host
        Write-Host "=== System Resources ==="
        
        # CPU Usage
        $cpu = Get-CimInstance -ClassName Win32_Processor | Measure-Object -Property LoadPercentage -Average
        Write-Host "CPU Usage: $($cpu.Average)%"
        
        # Memory Usage
        $mem = Get-CimInstance -ClassName Win32_OperatingSystem
        $totalMem = [math]::Round($mem.TotalVisibleMemorySize / 1MB, 2)
        $freeMem = [math]::Round($mem.FreePhysicalMemory / 1MB, 2)
        $usedMem = $totalMem - $freeMem
        Write-Host "Memory Usage: $usedMem GB / $totalMem GB"
        
        # Chrome Processes
        $chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
        Write-Host "Chrome Processes: $($chromeProcesses.Count)"
        
        Start-Sleep -Seconds 5
    }
}

# Pre-flight checks
function PreflightChecks {
    Write-Host "🔍 Running pre-flight checks..."
    
    # Check if we're in the right directory
    if (-not (Test-Path "manage.py")) {
        Write-Host "❌ Error: manage.py not found. Please run this script from your Django project directory." -ForegroundColor Red
        return $false
    }
    
    # Check Python installation
    try {
        $pythonVersion = & $PYTHON_CMD --version 2>&1
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python not found. Please install Python and ensure it's in your PATH." -ForegroundColor Red
        return $false
    }
    
    # Check Chrome installation
    $chromeInstalled = Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe"
    $chromeInstalled = $chromeInstalled -or (Test-Path "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    
    if ($chromeInstalled) {
        Write-Host "✅ Chrome found" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Chrome not installed. Select option 1 to install." -ForegroundColor Yellow
    }
    
    # Check Django
    try {
        & $PYTHON_CMD -c "import django; print(f'Django {django.get_version()}')" 2>$null
        Write-Host "✅ Django installation verified" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Django not found. Please install project requirements." -ForegroundColor Yellow
    }
    
    Write-Host ""
    return $true
}

# Main menu
function Show-MainMenu {
    Write-Host "Select an option:"
    Write-Host "1. Install Chrome & ChromeDriver"
    Write-Host "2. Install Python Dependencies"
    Write-Host "3. Run All Tests"
    Write-Host "4. Run Specific Test Categories"
    Write-Host "5. Cleanup Test Data Only"
    Write-Host "6. Monitor System Resources"
    Write-Host "7. Exit"
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-7)"
    
    switch ($choice) {
        1 {
            Install-Chrome
            Show-MainMenu
        }
        2 {
            Install-Dependencies
            Show-MainMenu
        }
        3 {
            Run-Tests
            Show-MainMenu
        }
        4 {
            Run-SpecificTests
            Show-MainMenu
        }
        5 {
            Cleanup-TestData
            Show-MainMenu
        }
        6 {
            Monitor-Resources
            Show-MainMenu
        }
        7 {
            Write-Host "👋 Goodbye!" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
            Show-MainMenu
        }
    }
}

# Display usage instructions
function Show-UsageInstructions {
    Write-Host "📖 USAGE INSTRUCTIONS:"
    Write-Host ""
    Write-Host "1. Open PowerShell as Administrator (recommended)"
    Write-Host "2. Navigate to your Django project directory"
    Write-Host "3. Run this script: .\live_domain_test.ps1"
    Write-Host ""
    Write-Host "4. Follow the menu prompts to install dependencies and run tests"
    Write-Host ""
    Write-Host "📝 NOTES:"
    Write-Host "- Tests will run in headless mode (no GUI) by default"
    Write-Host "- All test data will be cleaned up after tests complete"
    Write-Host "- Activity logs will be preserved for verification"
    Write-Host "- Tests include 2FA, organizations, mobile responsiveness, and email system"
    Write-Host ""
    Write-Host "🔧 COMMAND LINE USAGE:"
    Write-Host ".\live_domain_test.ps1 -Action run -AdminUser 'admin' -AdminPass 'password' -TestEmail 'test@domain.com'"
    Write-Host ""
}

# Handle command line arguments
switch ($Action.ToLower()) {
    "help" {
        Show-UsageInstructions
        exit 0
    }
    "install" {
        Install-Chrome
        Install-Dependencies
        exit 0
    }
    "run" {
        if ($AdminUser -and $AdminPass -and $TestEmail) {
            Run-Tests
        }
        else {
            Write-Host "❌ Missing required parameters for automated run" -ForegroundColor Red
            Show-UsageInstructions
        }
        exit 0
    }
    "cleanup" {
        Cleanup-TestData
        exit 0
    }
    default {
        # Welcome message
        Write-Host "🌐 Live Domain Testing Script for CRM System (Windows)"
        Write-Host "Domain: $DOMAIN_URL"
        Write-Host ""
        
        # Run pre-flight checks
        if (PreflightChecks) {
            # Start main menu
            Show-MainMenu
        }
        else {
            Write-Host "❌ Pre-flight checks failed. Please resolve the issues and try again." -ForegroundColor Red
            exit 1
        }
    }
}
