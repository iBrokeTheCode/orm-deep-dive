from django.shortcuts import render, redirect
from django.db.models import Sum, Prefetch
from django.utils import timezone

from .models import Restaurant, Sale, StaffRestaurants
from .forms import ProductOrderForm


def index(request):
    staff_restaurants = StaffRestaurants.objects.prefetch_related(
        'staff', 'restaurant')

    for record in staff_restaurants:
        print(record.restaurant.name)
        print(record.staff.name)

    return render(request, 'core/index.html')


def order_product(request):
    if request.method == 'POST':
        form = ProductOrderForm(request.POST)

        if form.is_valid():
            order = form.save()
            product = order.product
            product.number_in_stock -= order.number_of_items
            product.save()

            return redirect('core:order_product')
        else:
            return render(request, 'core/order_product.html', {'form': form})

    form = ProductOrderForm()

    context = {
        'form': form
    }

    return render(request, 'core/order_product.html', context)
