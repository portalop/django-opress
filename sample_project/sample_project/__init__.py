import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "[:SAMPLE_PROJECT:].settings")
import django
django.setup()

from photologue import adminwidgetswap
adminwidgetswap.swap_model_field()