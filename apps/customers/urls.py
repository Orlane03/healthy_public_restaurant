from django.urls import path
from apps.accounts import views as AccountViews
from . import views


urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('customer/profile/', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='customer_my_orders'),
    path('my_reservations/', views.my_reservations, name='customer_my_reservations'),
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
]