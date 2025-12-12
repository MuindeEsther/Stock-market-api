from django.core.management.base import BaseCommand
from scripts.fetch_stock_data import StockDataFetcher


class Command(BaseCommand):
    help = 'Fetch stock data from Yahoo Finance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tickers',
            type=str,
            help='Comma-separated list of ticker symbols'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='File containing ticker symbols (one per line)'
        )
        parser.add_argument(
            '--period',
            type=str,
            default='1y',
            help='Historical data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)'
        )
        parser.add_argument(
            '--update-all',
            action='store_true',
            help='Update all existing stocks'
        )
        parser.add_argument(
            '--popular',
            action='store_true',
            help='Fetch popular stocks (FAANG, etc.)'
        )

    def handle(self, *args, **options):
        fetcher = StockDataFetcher()
        
        if options['update_all']:
            self.stdout.write(self.style.WARNING('Updating all stocks in database...'))
            success, failed = fetcher.update_all_stocks(period=options['period'])
            self.stdout.write(self.style.SUCCESS(
                f'Update complete: {success} successful, {failed} failed'
            ))
        
        elif options['popular']:
            popular_tickers = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
                'TSLA', 'NVDA', 'JPM', 'V', 'WMT',
                'JNJ', 'PG', 'MA', 'DIS', 'NFLX',
                'PYPL', 'ADBE', 'CRM', 'INTC', 'CSCO'
            ]
            self.stdout.write(f'Fetching {len(popular_tickers)} popular stocks...')
            results = fetcher.fetch_multiple_stocks(popular_tickers, period=options['period'])
            self.stdout.write(self.style.SUCCESS(
                f"Results: {len(results['success'])} successful, {len(results['failed'])} failed"
            ))
        
        elif options['tickers']:
            tickers = [t.strip().upper() for t in options['tickers'].split(',')]
            self.stdout.write(f'Fetching {len(tickers)} stocks...')
            results = fetcher.fetch_multiple_stocks(tickers, period=options['period'])
            self.stdout.write(self.style.SUCCESS(
                f"Results: {len(results['success'])} successful, {len(results['failed'])} failed"
            ))
        
        elif options['file']:
            try:
                with open(options['file'], 'r') as f:
                    tickers = [line.strip().upper() for line in f if line.strip()]
                self.stdout.write(f'Fetching {len(tickers)} stocks from file...')
                results = fetcher.fetch_multiple_stocks(tickers, period=options['period'])
                self.stdout.write(self.style.SUCCESS(
                    f"Results: {len(results['success'])} successful, {len(results['failed'])} failed"
                ))
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f"File '{options['file']}' not found"))
        
        else:
            self.stdout.write(self.style.ERROR(
                'Please specify --tickers, --file, --popular, or --update-all'
            ))