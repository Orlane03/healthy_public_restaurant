from django.urls import path, include
from . import views
from apps.accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),
    
    # category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    
    # FoodItem CRUD
    path('menu-builder/food/add/', views.add_food, name='add_food'),
    path('menu-builder/food/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('menu-builder/food/delete/<int:pk>/', views.delete_food, name='delete_food'),
    
    # Opening Hour CRUD
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name='remove_opening_hours'),
    
    path('order_detail/<int:order_number>/', views.order_detail, name='vendor_order_detail'),
    path('order_delete/<int:order_number>/', views.order_delete, name='vendor_order_delete'),
    path('my_orders/', views.my_orders, name='vendor_my_orders'),

    path('my_reservations/', views.my_reservations, name='vendor_my_reservations'),

    path('table-builder/', views.table_builder, name='table_builder'),
    path('table-builder/add/', views.add_table, name='add_table'),
    path('table-builder/edit/<int:pk>/', views.edit_table, name='edit_table'),
    path('table-builder/delete/<int:pk>/', views.delete_table, name='delete_table'),

    path('<slug:vendor_slug>/tables/', views.vendor_tables, name='vendor_tables'),
    path('<slug:vendor_slug>/tables/<str:table_number>', views.vendor_table_detail, name='vendor_table_detail'),
    path('tables/place-table/<int:pk>', views.place_order_table, name='place_order_table'),
]

