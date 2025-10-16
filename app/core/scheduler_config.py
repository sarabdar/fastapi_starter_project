"""

-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
THIS FILE IS FOR CRONJOBS SO, IF YOUR PROJECT DOESN'T HAVE THE NEED THEN DELETE THIS FILE
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------



Scheduler Configuration
Centralized configuration for APScheduler with production-ready settings
"""

from typing import Dict, Any
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from pytz import timezone


from app.core.config import settings


class SchedulerConfig:
    """
    APScheduler configuration for production environment.
    
    Features:
    - Timezone-aware scheduling (configurable via environment)
    - Thread pool for I/O-bound tasks
    - Process pool for CPU-bound tasks
    - Graceful shutdown handling
    - Job persistence (memory-based, can be upgraded to database)
    """
    
    # Timezone - dynamically loaded from settings
    @classmethod
    def get_timezone(cls):
        """Get timezone from settings (environment variable)"""
        return timezone(settings.SCHEDULER_TIMEZONE)
    
    # Job stores configuration
    JOBSTORES: Dict[str, Any] = {
        'default': MemoryJobStore()
        # For production with persistence, use:
        # 'default': SQLAlchemyJobStore(url='postgresql://...')
    }
    
    # Executors configuration
    EXECUTORS: Dict[str, Any] = {
        'default': ThreadPoolExecutor(max_workers=settings.MAX_THEADPOOLING_WORKERS),  # For I/O-bound tasks
        'processpool': ProcessPoolExecutor(max_workers=settings.MAX_PROCESSPOOlEXECUTOR)  # For CPU-bound tasks
    }
    
    # Job defaults
    JOB_DEFAULTS: Dict[str, Any] = {
        'coalesce': True,  # Combine multiple pending executions into one
        'max_instances': 1,  # Prevent concurrent execution of same job
        'misfire_grace_time': 300  # 5 minutes grace period for missed jobs
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Get complete scheduler configuration.
        
        Returns:
            Dictionary with jobstores, executors, job_defaults, and timezone
        """
        return {
            'jobstores': cls.JOBSTORES,
            'executors': cls.EXECUTORS,
            'job_defaults': cls.JOB_DEFAULTS,
            'timezone': cls.get_timezone()
        }
