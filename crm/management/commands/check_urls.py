from django.core.management.base import BaseCommand
from django.urls import get_resolver
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check all URL patterns for consistency'
    
    def handle(self, *args, **options):
        self.stdout.write("Checking URL patterns...")
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        
        # Track all named URL patterns
        url_names = set()
        issues = []
        
        # Check for duplicate names
        for pattern in url_patterns:
            if hasattr(pattern, 'name') and pattern.name:
                if pattern.name in url_names:
                    issues.append(f"Duplicate URL name: {pattern.name}")
                url_names.add(pattern.name)
        
        # Check for common URL names that should exist
        required_urls = {'dashboard', 'verify_2fa', 'setup_2fa', 'recovery_code'}
        missing = required_urls - url_names
        
        if missing:
            issues.append(f"Missing required URL names: {', '.join(missing)}")
        
        if issues:
            for issue in issues:
                self.stdout.write(self.style.ERROR(issue))
            self.stdout.write(self.style.ERROR("URL pattern check complete with issues."))
        else:
            self.stdout.write(self.style.SUCCESS("URL pattern check complete. No issues found."))
