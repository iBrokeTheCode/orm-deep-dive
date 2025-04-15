from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('order-product/', views.order_product, name='order_product'),
    path('restaurant-detail/<int:pk>',
         views.restaurant_detail, name='restaurant_detail'),
]
