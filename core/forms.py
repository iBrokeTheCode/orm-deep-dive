from django import forms

from .models import Rating, Restaurant, Order


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('restaurant', 'user', 'rating')


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ('name', 'restaurant_type')


class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('product', 'number_of_items')
