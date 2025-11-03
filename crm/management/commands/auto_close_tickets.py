"""
Management command to automatically close resolved tickets after 3 business days
Run this command daily via cron to auto-close tickets that have been resolved for 3+ business days
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from crm.models import Ticket, ActivityLog
import logging

logger = logging.getLogger(__name__)


def calculate_business_days_ago(num_days):
    """
    Calculate the datetime that was num_days business days ago (excluding weekends)
    """
    current_date = timezone.now()
    business_days_counted = 0
    
    while business_days_counted < num_days:
        current_date -= timedelta(days=1)
        # Check if it's a weekday (Monday=0, Sunday=6)
        if current_date.weekday() < 5:  # Monday to Friday
            business_days_counted += 1
    
    return current_date


class Command(BaseCommand):
    help = 'Automatically closes tickets that have been resolved for 3+ business days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be closed without actually closing tickets',
        )
        parser.add_argument(
            '--business-days',
            type=int,
            default=3,
            help='Number of business days after which resolved tickets should be auto-closed (default: 3)',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=None,
            help='Number of hours after which resolved tickets should be auto-closed (overrides --business-days)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hours = options['hours']
        business_days = options['business_days']
        
        # Determine cutoff time based on parameters
        if hours is not None:
            # If hours specified, use that (backwards compatibility)
            cutoff_time = timezone.now() - timedelta(hours=hours)
            time_description = f'{hours} hours'
        else:
            # Use business days (default: 3 business days)
            cutoff_time = calculate_business_days_ago(business_days)
            time_description = f'{business_days} business days'
        
        self.stdout.write(self.style.WARNING(f'\n{"=" * 70}'))
        self.stdout.write(self.style.WARNING(f'AUTO-CLOSE RESOLVED TICKETS (after {time_description})'))
        self.stdout.write(self.style.WARNING(f'{"=" * 70}\n'))
        
        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 DRY RUN MODE - No changes will be made\n'))
        
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
            age_days = age_hours / 24
            
            self.stdout.write(
                f'  • Ticket #{ticket.id}: "{ticket.title}" '
                f'(resolved {age_days:.1f} days ago by {ticket.assigned_to or "unassigned"})'
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
                                  f"(brak potwierdzenia od klienta przez {time_description})",
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
