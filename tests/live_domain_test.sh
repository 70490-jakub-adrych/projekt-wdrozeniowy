#!/bin/bash

# SSH Live Domain Testing Deployment Script
# This script helps you run comprehensive tests on your live domain via SSH

echo "==================================="
echo "🚀 Live Domain Testing Setup"
echo "==================================="

# Configuration
DOMAIN_URL="https://dev.betulait.usermd.net"
PROJECT_PATH="/path/to/your/django/project"  # Update this path
VENV_PATH="/path/to/your/venv"  # Update this path

echo "Domain: $DOMAIN_URL"
echo "Project Path: $PROJECT_PATH"
echo ""

# Function to install Chrome and ChromeDriver
install_chrome() {
    echo "📦 Installing Chrome and ChromeDriver..."
    
    # Update system
    sudo apt-get update
    
    # Install Chrome
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
    
    # Install ChromeDriver
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}/chromedriver_linux64.zip"
    sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
    
    echo "✅ Chrome and ChromeDriver installed"
}

# Function to install Python dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."
    
    # Activate virtual environment
    source $VENV_PATH/bin/activate
    
    # Install testing dependencies
    pip install selenium==4.15.0
    pip install pytest==7.4.3
    pip install pytest-django==4.7.0
    pip install webdriver-manager==4.0.1
    pip install pyotp==2.9.0
    pip install Pillow
    pip install qrcode
    
    echo "✅ Python dependencies installed"
}

# Function to run comprehensive tests
run_tests() {
    echo "🧪 Running Comprehensive Live Domain Tests..."
    
    cd $PROJECT_PATH
    source $VENV_PATH/bin/activate
    
    # Prompt for admin credentials
    echo ""
    echo "Enter admin credentials for testing:"
    read -p "Admin Username: " ADMIN_USER
    read -s -p "Admin Password: " ADMIN_PASS
    echo ""
    read -p "Test Email Address: " TEST_EMAIL
    echo ""
    
    # Run the comprehensive test
    python manage.py comprehensive_live_test \
        --username="$ADMIN_USER" \
        --password="$ADMIN_PASS" \
        --domain="$DOMAIN_URL" \
        --headless
    
    echo ""
    echo "🏁 Test execution completed!"
}

# Function to run specific test categories
run_specific_tests() {
    echo "🎯 Select specific test categories to run:"
    echo "1. Authentication & Security Tests"
    echo "2. 2FA System Tests"
    echo "3. Organization Management Tests"
    echo "4. Email System Tests"
    echo "5. Mobile Responsiveness Tests"
    echo "6. All Tests"
    echo ""
    read -p "Enter your choice (1-6): " choice
    
    cd $PROJECT_PATH
    source $VENV_PATH/bin/activate
    
    case $choice in
        1)
            echo "Running Authentication & Security Tests..."
            # Add specific test command here
            ;;
        2)
            echo "Running 2FA System Tests..."
            # Add specific test command here
            ;;
        3)
            echo "Running Organization Management Tests..."
            # Add specific test command here
            ;;
        4)
            echo "Running Email System Tests..."
            # Add specific test command here
            ;;
        5)
            echo "Running Mobile Responsiveness Tests..."
            # Add specific test command here
            ;;
        6)
            run_tests
            ;;
        *)
            echo "Invalid choice. Running all tests..."
            run_tests
            ;;
    esac
}

# Function to cleanup test data
cleanup_test_data() {
    echo "🧹 Cleaning up test data..."
    
    cd $PROJECT_PATH
    source $VENV_PATH/bin/activate
    
    # Prompt for admin credentials
    read -p "Admin Username: " ADMIN_USER
    read -s -p "Admin Password: " ADMIN_PASS
    echo ""
    
    python manage.py comprehensive_live_test \
        --username="$ADMIN_USER" \
        --password="$ADMIN_PASS" \
        --domain="$DOMAIN_URL" \
        --cleanup-only \
        --headless
    
    echo "✅ Cleanup completed"
}

# Function to monitor system resources
monitor_resources() {
    echo "📊 System Resource Monitoring During Tests..."
    echo "Press Ctrl+C to stop monitoring"
    
    while true; do
        clear
        echo "=== System Resources ==="
        echo "CPU Usage:"
        top -bn1 | grep "Cpu(s)" | awk '{print $2 $3 $4 $5 $6 $7 $8}'
        echo ""
        echo "Memory Usage:"
        free -h
        echo ""
        echo "Disk Usage:"
        df -h | head -5
        echo ""
        echo "Chrome Processes:"
        ps aux | grep chrome | wc -l
        echo ""
        sleep 5
    done
}

# Main menu
main_menu() {
    echo "Select an option:"
    echo "1. Install Chrome & ChromeDriver"
    echo "2. Install Python Dependencies"
    echo "3. Run All Tests"
    echo "4. Run Specific Test Categories"
    echo "5. Cleanup Test Data Only"
    echo "6. Monitor System Resources"
    echo "7. Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            install_chrome
            main_menu
            ;;
        2)
            install_dependencies
            main_menu
            ;;
        3)
            run_tests
            main_menu
            ;;
        4)
            run_specific_tests
            main_menu
            ;;
        5)
            cleanup_test_data
            main_menu
            ;;
        6)
            monitor_resources
            main_menu
            ;;
        7)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            main_menu
            ;;
    esac
}

# Pre-flight checks
preflight_checks() {
    echo "🔍 Running pre-flight checks..."
    
    # Check if we're in the right directory
    if [ ! -f "manage.py" ]; then
        echo "❌ Error: manage.py not found. Please run this script from your Django project directory."
        echo "Update PROJECT_PATH variable in this script or cd to your Django project."
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        echo "⚠️  Warning: Virtual environment not found at $VENV_PATH"
        echo "Please update VENV_PATH variable in this script."
    fi
    
    # Check Chrome installation
    if ! command -v google-chrome &> /dev/null; then
        echo "⚠️  Chrome not installed. Select option 1 to install."
    else
        echo "✅ Chrome found: $(google-chrome --version)"
    fi
    
    # Check ChromeDriver
    if ! command -v chromedriver &> /dev/null; then
        echo "⚠️  ChromeDriver not installed. Select option 1 to install."
    else
        echo "✅ ChromeDriver found: $(chromedriver --version)"
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 not found. Please install Python3."
        exit 1
    else
        echo "✅ Python found: $(python3 --version)"
    fi
    
    echo ""
}

# Display usage instructions
usage_instructions() {
    echo "📖 USAGE INSTRUCTIONS:"
    echo ""
    echo "1. Update the configuration variables at the top of this script:"
    echo "   - DOMAIN_URL: Your live domain URL"
    echo "   - PROJECT_PATH: Path to your Django project"
    echo "   - VENV_PATH: Path to your Python virtual environment"
    echo ""
    echo "2. Upload this script to your server and make it executable:"
    echo "   chmod +x live_domain_test.sh"
    echo ""
    echo "3. Run the script:"
    echo "   ./live_domain_test.sh"
    echo ""
    echo "4. Follow the menu prompts to install dependencies and run tests"
    echo ""
    echo "📝 NOTES:"
    echo "- Tests will run in headless mode (no GUI) by default"
    echo "- All test data will be cleaned up after tests complete"
    echo "- Activity logs will be preserved for verification"
    echo "- Tests include 2FA, organizations, mobile responsiveness, and email system"
    echo ""
}

# Check if this is the first run
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    usage_instructions
    exit 0
fi

# Welcome message
echo "🌐 Live Domain Testing Script for CRM System"
echo "Domain: $DOMAIN_URL"
echo ""

# Run pre-flight checks
preflight_checks

# Start main menu
main_menu
