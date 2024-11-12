from django.urls import path
from . import views

urlpatterns = [
    path('reservation/confirm/', views.confirmation_reservation, name='confirmation_reservation'),
    # path('order_complete/<str:order_number>', views.order_complete, name='order_complete'),
    # path('confirm_payment/<str:order_number>/', views.confirm_payment, name='confirm_payment'),
    # path('my_orders/', views.my_orders, name='my_orders'),  # URL pour accéder à my_orders
]
