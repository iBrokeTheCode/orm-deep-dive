from django.contrib import admin

from .models import Restaurant, Rating, Sale, Product, Order, Comment


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'rating')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'content_object')


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Comment, CommentAdmin)
