"""
Management command to start the APScheduler for automatic stock data updates
Run with: python manage.py start_scheduler
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import atexit
from datetime import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start the APScheduler for automatic stock updates'
    
    scheduler = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--time',
            type=str,
            default='09:00',
            help='Time to run daily update in HH:MM format (default: 09:00)',
        )

    def handle(self, *args, **options):
        """Start the background scheduler"""
        update_time = options['time']
        
        # Parse the time
        try:
            hour, minute = map(int, update_time.split(':'))
        except ValueError:
            self.stdout.write(self.style.ERROR(f'Invalid time format. Use HH:MM (e.g., 09:00)'))
            return
        
        self.stdout.write(self.style.SUCCESS('Starting APScheduler for automatic stock updates...'))
        self.stdout.write(f'Daily update scheduled for {hour:02d}:{minute:02d}')
        
        # Initialize scheduler
        scheduler = BackgroundScheduler()
        
        # Add the daily update job
        scheduler.add_job(
            self.run_daily_update,
            CronTrigger(hour=hour, minute=minute),
            id='daily_stock_update',
            name='Daily Stock Data Update',
            replace_existing=True,
        )
        
        # Start the scheduler
        try:
            scheduler.start()
            self.stdout.write(
                self.style.SUCCESS('APScheduler started successfully!')
            )
            self.stdout.write('Press Ctrl+C to stop the scheduler.')
            
            # Keep the scheduler running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nShutting down scheduler...'))
                scheduler.shutdown()
                self.stdout.write(self.style.SUCCESS('Scheduler stopped.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error starting scheduler: {e}'))
            logger.exception('Error starting APScheduler')

    def run_daily_update(self):
        """Execute the daily stock update"""
        from scripts.fetch_stock_data import StockDataFetcher
        from scripts.calculate_indicators import TechnicalIndicatorCalculator
        
        try:
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(f'Starting Daily Update - {datetime.now()}')
            self.stdout.write(f'{"="*60}\n')
            
            # Step 1: Update stock prices
            self.stdout.write('Step 1: Updating stock prices...')
            fetcher = StockDataFetcher()
            success, failed = fetcher.update_all_stocks(period='5d')
            self.stdout.write(self.style.SUCCESS(
                f'Price update: {success} successful, {failed} failed\n'
            ))
            
            # Step 2: Calculate indicators
            self.stdout.write('Step 2: Calculating technical indicators...')
            calculator = TechnicalIndicatorCalculator()
            success, failed = calculator.calculate_for_all_stocks(days=90)
            self.stdout.write(self.style.SUCCESS(
                f'Indicator calculation: {success} successful, {failed} failed\n'
            ))
            
            self.stdout.write(self.style.SUCCESS(f'{"="*60}'))
            self.stdout.write(self.style.SUCCESS(f'Daily Update Complete - {datetime.now()}'))
            self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))
            
            logger.info('Daily stock update completed successfully')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during daily update: {e}'))
            logger.exception('Error during daily update')
