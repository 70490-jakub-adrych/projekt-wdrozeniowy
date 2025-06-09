# PowerShell script to download static files from GitHub repository

# Create directory structure for development
New-Item -Path "static/crm/css" -ItemType Directory -Force
New-Item -Path "static/crm/js" -ItemType Directory -Force
New-Item -Path "static/crm/webfonts" -ItemType Directory -Force

# Create directory structure for production (myDevil hosting)
New-Item -Path "public/static/crm/css" -ItemType Directory -Force
New-Item -Path "public/static/crm/js" -ItemType Directory -Force
New-Item -Path "public/static/crm/webfonts" -ItemType Directory -Force
New-Item -Path "public/media" -ItemType Directory -Force

Write-Host "Downloading static files from GitHub repository..." -ForegroundColor Green

# Base URL for your static files repository
$BaseUrl = "https://raw.githubusercontent.com/70490-jakub-adrych/static/main/static"

# Download CSS files to both locations
Write-Host "Downloading CSS files..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "$BaseUrl/crm/css/bootstrap.min.css" -OutFile "static/crm/css/bootstrap.min.css"
Invoke-WebRequest -Uri "$BaseUrl/crm/css/all.min.css" -OutFile "static/crm/css/all.min.css"
Invoke-WebRequest -Uri "$BaseUrl/crm/css/bootstrap.min.css" -OutFile "public/static/crm/css/bootstrap.min.css"
Invoke-WebRequest -Uri "$BaseUrl/crm/css/all.min.css" -OutFile "public/static/crm/css/all.min.css"

# Download JS files to both locations
Write-Host "Downloading JavaScript files..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "$BaseUrl/crm/js/bootstrap.min.js" -OutFile "static/crm/js/bootstrap.min.js"
Invoke-WebRequest -Uri "$BaseUrl/crm/js/jquery-3.5.1.slim.min.js" -OutFile "static/crm/js/jquery-3.5.1.slim.min.js"
Invoke-WebRequest -Uri "$BaseUrl/crm/js/popper.min.js" -OutFile "static/crm/js/popper.min.js"
Invoke-WebRequest -Uri "$BaseUrl/crm/js/bootstrap.min.js" -OutFile "public/static/crm/js/bootstrap.min.js"
Invoke-WebRequest -Uri "$BaseUrl/crm/js/jquery-3.5.1.slim.min.js" -OutFile "public/static/crm/js/jquery-3.5.1.slim.min.js"
Invoke-WebRequest -Uri "$BaseUrl/crm/js/popper.min.js" -OutFile "public/static/crm/js/popper.min.js"

# Download Font Awesome webfonts to both locations
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
    Invoke-WebRequest -Uri "$BaseUrl/crm/webfonts/$font" -OutFile "public/static/crm/webfonts/$font"
}

Write-Host "All static files downloaded successfully!" -ForegroundColor Green
Write-Host "Files downloaded to both 'static/' (for development) and 'public/static/' (for production)" -ForegroundColor Green
# End of script