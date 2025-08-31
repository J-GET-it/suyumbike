from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from bot import bot
from bot.models import User, Category, Place


class Command(BaseCommand):
    help = "Clearing dayly clicks"

    def handle(self, *args, **options):
        categories = Category.objects.all()
        for category in categories:
            category.prev_day_clicks = category.day_clicks
            category.day_clicks = 0
            category.save()

        places = Place.objects.all()
        for place in places:
            place.prev_day_clicks = place.day_clicks
            place.day_clicks = 0
            place.save()