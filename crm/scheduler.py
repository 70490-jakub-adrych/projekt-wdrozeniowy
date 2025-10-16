"""
Auto-close tickets scheduler using APScheduler
This runs as part of Django application - no cron needed!
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management import call_command
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
import logging

logger = logging.getLogger(__name__)


def auto_close_resolved_tickets():
    """
    Job that automatically closes resolved tickets after 24 hours
    """
    logger.info("Running auto_close_resolved_tickets job...")
    try:
        # Call the management command
        call_command('auto_close_tickets')
        logger.info("auto_close_resolved_tickets job completed successfully")
    except Exception as e:
        logger.error(f"Error in auto_close_resolved_tickets job: {e}")


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    Delete old job executions (older than 7 days by default)
    This prevents the database from filling up with old job execution records
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def start_scheduler():
    """
    Start the APScheduler
    """
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Schedule auto_close_tickets to run daily at 2 AM
    scheduler.add_job(
        auto_close_resolved_tickets,
        trigger=CronTrigger(hour=2, minute=0),  # Run at 2:00 AM every day
        id="auto_close_resolved_tickets",
        max_instances=1,
        replace_existing=True,
        name="Auto-close resolved tickets after 24 hours"
    )
    logger.info("Added job 'auto_close_resolved_tickets' to scheduler (runs daily at 2:00 AM)")
    
    # Schedule cleanup of old job executions weekly (Sunday at 3 AM)
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
        name="Delete old job execution records"
    )
    logger.info("Added job 'delete_old_job_executions' to scheduler (runs weekly on Sunday at 3:00 AM)")
    
    try:
        logger.info("Starting scheduler...")
        scheduler.start()
        logger.info("Scheduler started successfully")
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully")
