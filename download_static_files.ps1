# PowerShell script to download static files from GitHub repository

# Create directory structure
New-Item -Path "static/crm/css" -ItemType Directory -Force
New-Item -Path "static/crm/js" -ItemType Directory -Force
New-Item -Path "static/crm/webfonts" -ItemType Directory -Force

Write-Host "Downloading static files from GitHub repository..." -ForegroundColor Green

# Base URL for your static files repository
$BaseUrl = "https://raw.githubusercontent.com/70490-jakub-adrych/static/main/static"

# Download CSS files
Write-Host "Downloading CSS files..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "$BaseUrl/crm/css/bootstrap.min.css" -OutFile "static/crm/css/bootstrap.min.css"
Invoke-WebRequest -Uri "$BaseUrl/crm/css/all.min.css" -OutFile "static/crm/css/all.min.css"

# Download JS files
Write-Host "Downloading JavaScript files..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "$BaseUrl/crm/js/bootstrap.min.js" -OutFile "static/crm/js/bootstrap.min.js"
Invoke-WebRequest -Uri "$BaseUrl/crm/js/jquery-3.5.1.slim.min.js" -OutFile "static/crm/js/jquery-3.5.1.slim.min.js"
Invoke-WebRequest -Uri "$BaseUrl/crm/js/popper.min.js" -OutFile "static/crm/js/popper.min.js"

# Download Font Awesome webfonts
Write-Host "Downloading Font Awesome webfonts..." -ForegroundColor Yellow
$webfonts = @(
    "fa-brands-400.eot",
    "fa-brands-400.svg", 
    "fa-brands-400.ttf",
    "fa-brands-400.woff",
    "fa-brands-400.woff2",
    "fa-regular-400.eot",
    "fa-regular-400.svg",
    "fa-regular-400.ttf", 
    "fa-regular-400.woff",
    "fa-regular-400.woff2",
    "fa-solid-900.eot",
    "fa-solid-900.svg",
    "fa-solid-900.ttf",
    "fa-solid-900.woff",
    "fa-solid-900.woff2"
)

foreach ($font in $webfonts) {
    Write-Host "  Downloading $font..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "$BaseUrl/crm/webfonts/$font" -OutFile "static/crm/webfonts/$font"
}

Write-Host "All static files downloaded successfully!" -ForegroundColor Green
# End of script