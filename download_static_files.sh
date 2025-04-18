#!/bin/bash

# Create directory structure
mkdir -p static/crm/css
mkdir -p static/crm/js
mkdir -p static/crm/webfonts

# Download Bootstrap
wget https://github.com/twbs/bootstrap/releases/download/v4.5.2/bootstrap-4.5.2-dist.zip
unzip bootstrap-4.5.2-dist.zip
cp bootstrap-4.5.2-dist/css/bootstrap.min.css static/crm/css/
cp bootstrap-4.5.2-dist/js/bootstrap.min.js static/crm/js/
rm -rf bootstrap-4.5.2-dist bootstrap-4.5.2-dist.zip

# Download jQuery
wget -O static/crm/js/jquery-3.5.1.slim.min.js https://code.jquery.com/jquery-3.5.1.slim.min.js

# Download Popper.js
wget -O static/crm/js/popper.min.js https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js

# Download Font Awesome
wget https://use.fontawesome.com/releases/v5.15.1/fontawesome-free-5.15.1-web.zip
unzip fontawesome-free-5.15.1-web.zip
cp fontawesome-free-5.15.1-web/css/all.min.css static/crm/css/
cp -r fontawesome-free-5.15.1-web/webfonts/* static/crm/webfonts/
rm -rf fontawesome-free-5.15.1-web fontawesome-free-5.15.1-web.zip

echo "All static files downloaded successfully!"
