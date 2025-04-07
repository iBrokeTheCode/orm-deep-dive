from django.contrib import admin

from .models import Restaurant, Rating, Sale

admin.site.register(Restaurant)
admin.site.register(Rating)
admin.site.register(Sale)
