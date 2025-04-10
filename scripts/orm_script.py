from django.db import connection

from pprint import pprint

from core.models import Staff, Restaurant


def run():
    pass


# Add salary field to M2M relationship / through
# Delete db/ migrations and cache
# Repopulate
# Create associations with the new table
# Same methods
# add method set null value in salary / through_defaults = {'salary': 28_000}
# set 10 items
# prefetch
