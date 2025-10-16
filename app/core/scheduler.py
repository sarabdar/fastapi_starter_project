"""
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
THIS FILE IS FOR CRONJOBS SO, IF YOUR PROJECT DOESN'T HAVE THE NEED THEN DELETE THIS FILE
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------


Scheduler Manager
Centralized scheduler initialization and job registration for APScheduler





"""

from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings

from app.core.scheduler_config import SchedulerConfig
from app.core.logger import get_logger


# Import jobs from cron_jobs
# from app.cron_jobs.job import cleanup_old_data, generate_daily_reports, backup_critical_data, send_daily_notifications

logger = get_logger(__name__)


class SchedulerManager:
    """
    Manages the APScheduler instance and job registration.
    
    Features:
    - Singleton pattern for scheduler instance
    - Centralized job registration
    - Graceful startup and shutdown
    - Error handling and logging
    - Production-ready configuration
    
    Usage:
        scheduler_manager = SchedulerManager()
        await scheduler_manager.start()
        # ... application runs ...
        await scheduler_manager.shutdown()
    """
    
    _instance: Optional['SchedulerManager'] = None
    _scheduler: Optional[AsyncIOScheduler] = None
    
    def __new__(cls):
        """Singleton pattern - only one scheduler instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize scheduler with configuration"""
        if self._scheduler is None:
            config = SchedulerConfig.get_config()
            self._scheduler = AsyncIOScheduler(**config)
            logger.info("Scheduler initialized with timezone: %s", config['timezone'])
    
    def register_jobs(self) -> None:
        """
        Register all scheduled jobs with the scheduler.
        
        This method defines all cron jobs and their schedules.
        Add new jobs here as needed.
        """
        try:
            # Low stock notifications job - runs at configured time
            job_timezone = SchedulerConfig.get_timezone()
            
            
            
            # --------------------------------------------------------------------
            # --------------------------------------------------------------------
            # PLEASE ADD YOUR JOB LIKE SHOWN IN THE EXAMPLE BELOW
            # --------------------------------------------------------------------
            # --------------------------------------------------------------------
            
            
            # EXAMPLE : 
            
            # self._scheduler.add_job(
            #     func=run_nightly_maintenance,
            #     trigger=CronTrigger(
            #         hour=settings.LOW_STOCK_WHATSAPP_MSG_JOB_HOUR,
            #         minute=settings.LOW_STOCK_WHATSAPP_MSG_JOB_MINUTE,
            #         timezone=job_timezone
            #     ),
            #     id='low_stock_notifications',
            #     name='Low Stock Notifications',
            #     replace_existing=True,
            #     max_instances=1
            # )
            # logger.info(
            #     "Registered job: Low Stock Notifications (runs at %02d:%02d %s daily)",
            #     settings.LOW_STOCK_WHATSAPP_MSG_JOB_HOUR,
            #     settings.LOW_STOCK_WHATSAPP_MSG_JOB_MINUTE,
            #     settings.SCHEDULER_TIMEZONE
            # )
            

            
            logger.info("All scheduled jobs registered successfully")
            
        except Exception as e:
            logger.exception("Error registering scheduled jobs: %s", str(e))
            raise
    
    async def start(self) -> None:
        """
        Start the scheduler and begin executing jobs.
        
        This should be called during application startup.
        
        Raises:
            Exception: If scheduler fails to start
        """
        try:
            if self._scheduler and not self._scheduler.running:
                self.register_jobs()
                self._scheduler.start()
                logger.info("=" * 60)
                logger.info("Scheduler started successfully")
                logger.info("Registered jobs:")
                for job in self._scheduler.get_jobs():
                    logger.info("  - %s (ID: %s) - Next run: %s", 
                              job.name, job.id, job.next_run_time)
                logger.info("=" * 60)
            else:
                logger.warning("Scheduler is already running")
        except Exception as e:
            logger.exception("Failed to start scheduler: %s", str(e))
            raise
    
    async def shutdown(self, wait: bool = True) -> None:
        """
        Gracefully shutdown the scheduler.
        
        This should be called during application shutdown.
        
        Args:
            wait: If True, wait for all running jobs to complete
        """
        try:
            if self._scheduler and self._scheduler.running:
                logger.info("Shutting down scheduler...")
                self._scheduler.shutdown(wait=wait)
                logger.info("Scheduler shut down successfully")
            else:
                logger.warning("Scheduler is not running")
        except Exception as e:
            logger.exception("Error shutting down scheduler: %s", str(e))
    
    def pause_job(self, job_id: str) -> None:
        """
        Pause a specific job.
        
        Args:
            job_id: ID of the job to pause
        """
        try:
            self._scheduler.pause_job(job_id)
            logger.info("Job '%s' paused", job_id)
        except Exception as e:
            logger.error("Failed to pause job '%s': %s", job_id, str(e))
    
    def resume_job(self, job_id: str) -> None:
        """
        Resume a paused job.
        
        Args:
            job_id: ID of the job to resume
        """
        try:
            self._scheduler.resume_job(job_id)
            logger.info("Job '%s' resumed", job_id)
        except Exception as e:
            logger.error("Failed to resume job '%s': %s", job_id, str(e))
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Get status information for a specific job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job information or None if not found
        """
        try:
            job = self._scheduler.get_job(job_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': str(job.next_run_time),
                    'trigger': str(job.trigger)
                }
            return None
        except Exception as e:
            logger.error("Failed to get job status for '%s': %s", job_id, str(e))
            return None
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is currently running"""
        return self._scheduler.running if self._scheduler else False


# Global scheduler instance
scheduler_manager = SchedulerManager()
