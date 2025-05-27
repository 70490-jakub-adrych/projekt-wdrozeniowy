#!/bin/bash

# Create directory structure
mkdir -p static/crm/css
mkdir -p static/crm/js
mkdir -p static/crm/webfonts

echo "Downloading static files from GitHub repository..."

# Base URL for your static files repository
BASE_URL="https://raw.githubusercontent.com/70490-jakub-adrych/static/main/static"

# Download CSS files
echo "Downloading CSS files..."
wget -O static/crm/css/bootstrap.min.css "$BASE_URL/crm/css/bootstrap.min.css"
wget -O static/crm/css/all.min.css "$BASE_URL/crm/css/all.min.css"

# Download JS files
echo "Downloading JavaScript files..."
wget -O static/crm/js/bootstrap.min.js "$BASE_URL/crm/js/bootstrap.min.js"
wget -O static/crm/js/jquery-3.5.1.slim.min.js "$BASE_URL/crm/js/jquery-3.5.1.slim.min.js"
wget -O static/crm/js/popper.min.js "$BASE_URL/crm/js/popper.min.js"

# Download Font Awesome webfonts
echo "Downloading Font Awesome webfonts..."
wget -O static/crm/webfonts/fa-brands-400.eot "$BASE_URL/crm/webfonts/fa-brands-400.eot"
wget -O static/crm/webfonts/fa-brands-400.svg "$BASE_URL/crm/webfonts/fa-brands-400.svg"
wget -O static/crm/webfonts/fa-brands-400.ttf "$BASE_URL/crm/webfonts/fa-brands-400.ttf"
wget -O static/crm/webfonts/fa-brands-400.woff "$BASE_URL/crm/webfonts/fa-brands-400.woff"
wget -O static/crm/webfonts/fa-brands-400.woff2 "$BASE_URL/crm/webfonts/fa-brands-400.woff2"
wget -O static/crm/webfonts/fa-regular-400.eot "$BASE_URL/crm/webfonts/fa-regular-400.eot"
wget -O static/crm/webfonts/fa-regular-400.svg "$BASE_URL/crm/webfonts/fa-regular-400.svg"
wget -O static/crm/webfonts/fa-regular-400.ttf "$BASE_URL/crm/webfonts/fa-regular-400.ttf"
wget -O static/crm/webfonts/fa-regular-400.woff "$BASE_URL/crm/webfonts/fa-regular-400.woff"
wget -O static/crm/webfonts/fa-regular-400.woff2 "$BASE_URL/crm/webfonts/fa-regular-400.woff2"
wget -O static/crm/webfonts/fa-solid-900.eot "$BASE_URL/crm/webfonts/fa-solid-900.eot"
wget -O static/crm/webfonts/fa-solid-900.svg "$BASE_URL/crm/webfonts/fa-solid-900.svg"
wget -O static/crm/webfonts/fa-solid-900.ttf "$BASE_URL/crm/webfonts/fa-solid-900.ttf"
wget -O static/crm/webfonts/fa-solid-900.woff "$BASE_URL/crm/webfonts/fa-solid-900.woff"
wget -O static/crm/webfonts/fa-solid-900.woff2 "$BASE_URL/crm/webfonts/fa-solid-900.woff2"

echo "All static files downloaded successfully!"
