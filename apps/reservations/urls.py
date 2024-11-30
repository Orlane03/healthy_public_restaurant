from django.urls import path
from . import views

urlpatterns = [
    path('reservation/confirm/', views.confirmation_reservation, name='confirmation_reservation'),
    path('reservation_complete/<str:reservation_number>', views.reservation_complete, name='reservation_complete'),
    path('vendor/reservation_detail/<str:number>', views.reservation_detail, name='reservation_detail_vendor'),
    # path('confirm_payment/<str:order_number>/', views.confirm_payment, name='confirm_payment'),
    path('c_reservations/', views.c_reservations, name='c_reservations'),
]
