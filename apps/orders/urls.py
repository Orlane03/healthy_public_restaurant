from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('confirm_payment/<str:order_number>/', views.confirm_payment, name='confirm_payment'),
    path('my_orders/', views.my_orders, name='my_orders'),  # URL pour accéder à my_orders
]
