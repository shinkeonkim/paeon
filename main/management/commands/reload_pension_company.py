from django.core.management.base import BaseCommand
from main.utils import reload_pension_company

class Command(BaseCommand):
    help = 'Reload Pension Company'

    def handle(self, *args, **options):
        reload_pension_company()
        self.stdout.write(self.style.SUCCESS('Success'))
