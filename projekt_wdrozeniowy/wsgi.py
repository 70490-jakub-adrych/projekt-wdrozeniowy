"""
WSGI config for projekt_wdrozeniowy project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projekt_wdrozeniowy.settings')

application = get_wsgi_application()
