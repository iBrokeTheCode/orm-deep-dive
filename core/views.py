from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Prefetch
from django.utils import timezone
from django.db import transaction
from functools import partial

from .models import Restaurant, Sale, StaffRestaurants
from .forms import ProductOrderForm


def email_user(email: str):
    print(
        f'Dear user, thank you for your oder. Sending confirmation to {email}')


def index(request):
    restaurants = Restaurant.objects.all()[:5]

    context = {
        'restaurants': restaurants
    }

    return render(request, 'core/index.html', context)


def order_product(request):
    if request.method == 'POST':
        form = ProductOrderForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                order = form.save()

                # simulate crash
                # import sys
                # sys.exit(1)

                product = order.product
                product.number_in_stock -= order.number_of_items
                product.save()
            transaction.on_commit(partial(email_user, 'example@emai.com'))

            return redirect('core:order_product')
        else:
            return render(request, 'core/order_product.html', {'form': form})

    form = ProductOrderForm()

    context = {
        'form': form
    }

    return render(request, 'core/order_product.html', context)


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=7)
    context = {
        'restaurant': restaurant
    }
    return render(request, 'core/restaurant_detail.html', context)
