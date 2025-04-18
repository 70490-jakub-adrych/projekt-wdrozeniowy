# PowerShell script to download static files

# Create directory structure
New-Item -Path "static/crm/css" -ItemType Directory -Force
New-Item -Path "static/crm/js" -ItemType Directory -Force
New-Item -Path "static/crm/webfonts" -ItemType Directory -Force

# Download Bootstrap
$bootstrapUrl = "https://github.com/twbs/bootstrap/releases/download/v4.5.2/bootstrap-4.5.2-dist.zip"
$bootstrapZip = "bootstrap-4.5.2-dist.zip"
Invoke-WebRequest -Uri $bootstrapUrl -OutFile $bootstrapZip
Expand-Archive -Path $bootstrapZip -DestinationPath "."
Copy-Item "bootstrap-4.5.2-dist/css/bootstrap.min.css" -Destination "static/crm/css/"
Copy-Item "bootstrap-4.5.2-dist/js/bootstrap.min.js" -Destination "static/crm/js/"
Remove-Item -Path "bootstrap-4.5.2-dist" -Recurse -Force
Remove-Item -Path $bootstrapZip -Force

# Download jQuery
Invoke-WebRequest -Uri "https://code.jquery.com/jquery-3.5.1.slim.min.js" -OutFile "static/crm/js/jquery-3.5.1.slim.min.js"

# Download Popper.js
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" -OutFile "static/crm/js/popper.min.js"

# Download Font Awesome
$fontAwesomeUrl = "https://use.fontawesome.com/releases/v5.15.1/fontawesome-free-5.15.1-web.zip"
$fontAwesomeZip = "fontawesome-free-5.15.1-web.zip"
Invoke-WebRequest -Uri $fontAwesomeUrl -OutFile $fontAwesomeZip
Expand-Archive -Path $fontAwesomeZip -DestinationPath "."
Copy-Item "fontawesome-free-5.15.1-web/css/all.min.css" -Destination "static/crm/css/"
Copy-Item "fontawesome-free-5.15.1-web/webfonts/*" -Destination "static/crm/webfonts/" -Recurse
Remove-Item -Path "fontawesome-free-5.15.1-web" -Recurse -Force
Remove-Item -Path $fontAwesomeZip -Force

Write-Host "All static files downloaded successfully!" -ForegroundColor Green
