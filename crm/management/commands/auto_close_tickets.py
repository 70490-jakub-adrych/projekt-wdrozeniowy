"""
Management command to automatically close resolved tickets after 24 hours
Run this command daily via cron to auto-close tickets that have been resolved for 24+ hours
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from crm.models import Ticket, ActivityLog
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Automatically closes tickets that have been resolved for 24+ hours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be closed without actually closing tickets',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours after which resolved tickets should be auto-closed (default: 24)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hours = options['hours']
        
        self.stdout.write(self.style.WARNING(f'\n{"=" * 70}'))
        self.stdout.write(self.style.WARNING(f'AUTO-CLOSE RESOLVED TICKETS (after {hours} hours)'))
        self.stdout.write(self.style.WARNING(f'{"=" * 70}\n'))
        
        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 DRY RUN MODE - No changes will be made\n'))
        
        # Calculate the cutoff time
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Find tickets that are resolved and older than cutoff time
        tickets_to_close = Ticket.objects.filter(
            status='resolved',
            resolved_at__lte=cutoff_time
        )
        
        count = tickets_to_close.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No tickets need to be auto-closed'))
            return
        
        self.stdout.write(f'Found {count} ticket(s) to auto-close:\n')
        
        closed_count = 0
        error_count = 0
        
        for ticket in tickets_to_close:
            age_hours = (timezone.now() - ticket.resolved_at).total_seconds() / 3600
            
            self.stdout.write(
                f'  • Ticket #{ticket.id}: "{ticket.title}" '
                f'(resolved {age_hours:.1f}h ago by {ticket.assigned_to or "unassigned"})'
            )
            
            if not dry_run:
                try:
                    # Update ticket status
                    old_status = ticket.status
                    ticket.status = 'closed'
                    ticket.closed_at = timezone.now()
                    ticket.save()
                    
                    # Log the activity
                    ActivityLog.objects.create(
                        user=None,  # System action
                        action_type='ticket_closed',
                        description=f"Automatycznie zamknięto zgłoszenie '{ticket.title}' "
                                  f"(brak potwierdzenia od klienta przez {hours}h)",
                        ticket=ticket,
                        ip_address=None
                    )
                    
                    closed_count += 1
                    self.stdout.write(self.style.SUCCESS(f'    ✅ Closed'))
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'    ❌ Error: {str(e)}'))
                    logger.error(f'Error auto-closing ticket #{ticket.id}: {str(e)}')
        
        self.stdout.write(f'\n{"=" * 70}')
        
        if dry_run:
            self.stdout.write(self.style.NOTICE(f'Would close {count} ticket(s)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully closed: {closed_count}'))
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f'❌ Errors: {error_count}'))
        
        self.stdout.write(f'{"=" * 70}\n')
