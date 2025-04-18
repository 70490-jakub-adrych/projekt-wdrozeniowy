# Static Files Setup Instructions

## 1. Create Directory Structure

```bash
mkdir -p static/crm/css
mkdir -p static/crm/js
mkdir -p static/crm/webfonts
```

## 2. Download Required Libraries

### Bootstrap 4.5.2
Download from: https://github.com/twbs/bootstrap/releases/download/v4.5.2/bootstrap-4.5.2-dist.zip
Extract and copy:
- `css/bootstrap.min.css` to `static/crm/css/`
- `js/bootstrap.min.js` to `static/crm/js/`

### jQuery 3.5.1 Slim
Download from: https://code.jquery.com/jquery-3.5.1.slim.min.js
Save to `static/crm/js/jquery-3.5.1.slim.min.js`

### Popper.js 1.16.1
Download from: https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js
Save to `static/crm/js/popper.min.js`

### Font Awesome 5.15.1
Download from: https://use.fontawesome.com/releases/v5.15.1/fontawesome-free-5.15.1-web.zip
Extract and copy:
- `css/all.min.css` to `static/crm/css/`
- `webfonts/*` to `static/crm/webfonts/`

## 3. Collect Static Files

After placing all files in the correct directories, run:

```bash
python manage.py collectstatic
```

## 4. Verify

Start the development server and verify that all styles and scripts load correctly.
