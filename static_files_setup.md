# Static Files Setup Instructions

## Automated Download (Recommended)

### Linux/macOS
```bash
chmod +x download_static_files.sh
./download_static_files.sh
```

### Windows (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\download_static_files.ps1
```

## What Gets Downloaded

The scripts automatically download all required static files from our GitHub repository:

### CSS Files
- Bootstrap 4.5.2 (`bootstrap.min.css`)
- Font Awesome 5.15.1 (`all.min.css`)

### JavaScript Files
- jQuery 3.5.1 Slim (`jquery-3.5.1.slim.min.js`)
- Popper.js 1.16.1 (`popper.min.js`)
- Bootstrap 4.5.2 JS (`bootstrap.min.js`)

### Font Files
- Font Awesome webfonts (all variants: eot, svg, ttf, woff, woff2)

## Manual Download (Alternative)

If the scripts don't work, you can manually download files from:
https://github.com/70490-jakub-adrych/static/tree/main/static

1. Create directory structure:
```bash
mkdir -p static/crm/css
mkdir -p static/crm/js
mkdir -p static/crm/webfonts
```

2. Download individual files and place them in the correct directories

## Collect Static Files

After downloading, run Django's collectstatic command:

```bash
python manage.py collectstatic
```

## Verify

Start the development server and verify that all styles and scripts load correctly:

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ and check that:
- Bootstrap styling is applied
- Font Awesome icons appear correctly
- JavaScript interactions work
