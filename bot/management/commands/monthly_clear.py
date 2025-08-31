from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from bot import bot
from bot.models import User, Category, Place


class Command(BaseCommand):
    help = "Clearing dayly clicks"

    def handle(self, *args, **options):
        categories = Category.objects.all()
        for category in categories:
            category.prev_month_clicks = category.month_clicks
            category.month_clicks = 0
            category.save()

        places = Place.objects.all()
        for place in places:
            place.prev_month_clicks = place.month_clicks
            place.month_clicks = 0
            place.save()