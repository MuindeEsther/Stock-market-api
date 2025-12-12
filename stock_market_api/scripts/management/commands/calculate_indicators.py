from django.core.management.base import BaseCommand
from scripts.calculate_indicators import TechnicalIndicatorCalculator


class Command(BaseCommand):
    help = 'Calculate technical indicators for stocks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ticker',
            type=str,
            help='Stock ticker symbol'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Calculate for all stocks'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days of historical data to use (default: 365)'
        )

    def handle(self, *args, **options):
        calculator = TechnicalIndicatorCalculator()
        
        if options['all']:
            self.stdout.write(self.style.WARNING('Calculating indicators for all stocks...'))
            success, failed = calculator.calculate_for_all_stocks(days=options['days'])
            self.stdout.write(self.style.SUCCESS(
                f'Complete: {success} successful, {failed} failed'
            ))
        
        elif options['ticker']:
            self.stdout.write(f"Calculating indicators for {options['ticker']}...")
            if calculator.calculate_all_indicators(options['ticker'], days=options['days']):
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully calculated indicators for {options['ticker']}"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"Failed to calculate indicators for {options['ticker']}"
                ))
        
        else:
            self.stdout.write(self.style.ERROR(
                'Please specify --ticker or --all'
            ))