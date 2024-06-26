import os
import sys
import django
from django.core.management import call_command

# Ensure the settings module is set correctly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def dumpdata():
    sys.stdout.reconfigure(encoding='utf-8')
    call_command('dumpdata', '--natural-primary', '--natural-foreign', '--indent', '4', stdout=sys.stdout)

if __name__ == "__main__":
    dumpdata()
