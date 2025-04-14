from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Restaurant, Rating, Sale, Product, Order, Comment


class CommentInline(GenericTabularInline):
    model = Comment
    max_num = 1


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = (CommentInline, )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'rating')
    inlines = (CommentInline, )


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'content_object')


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Comment, CommentAdmin)
