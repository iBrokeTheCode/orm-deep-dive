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


class ProductStockException(Exception):
    pass


class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('product', 'number_of_items')

    def save(self, commit=True):
        order = super().save(commit=False)

        if order.number_of_items > order.product.number_in_stock:
            raise ProductStockException(
                f'Not enough items in stock for the product {order.product.name}')
        if commit:
            order.save()
        return order
