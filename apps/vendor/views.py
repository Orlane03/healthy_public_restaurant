from django.db import IntegrityError
from urllib import response
from django.shortcuts import get_object_or_404, render, redirect
from django.http.response import HttpResponse, JsonResponse
from .forms import VendorForm, OpeningHourForm, TableForm
from apps.accounts.forms import UserProfileForm
import simplejson as json
from apps.accounts.models import UserProfile
from .models import OpeningHour, Vendor, Table
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.accounts.views import check_role_vendor
from apps.menu.models import Category, FoodItem
from .utils import get_vendor
from apps.menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify
from apps.orders.models import Order, OrderedFood
from datetime import date, datetime
from django.db.models import Prefetch
from ..marketplace.context_processors import get_cart_amounts
from ..marketplace.models import Cart, Tax
from ..orders.forms import OrderForm
from ..orders.utils import generate_order_number
from ..reservations.forms import ReservationForm
from ..reservations.models import Reservations


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    print(profile.profile_picture)
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid ():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:     
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor' : vendor,
    }
    return render(request, 'vendor/vprofile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            
            category.save() # when the category object is saved the the category id will be generated
            category.slug = slugify(category_name)+'-'+str(category.id) #chicken-15 first is name second is category id
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request,'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')
    
    
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Item added successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # to display categories which belongs to logged in user
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Item updated successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        # to display categories which belongs to logged in user
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food,
    }
    return render(request,'vendor/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food Item has been deleted successfully!')
    return redirect('fooditems_by_category', food.category.id)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)

def add_opening_hours(request):
    # handle the data and save them inside the database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            
            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed )
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed':'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)
        else:
            HttpResponse('Invalid request')
       
            
def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':               
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})
        
        
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))
        vendor = Vendor.objects.get(user=request.user)


        print("ordered_food", ordered_food)

        print(order.get_total_by_vendor())

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'grand_total': order.get_total_by_vendor()['grand_total'],
        }
    except Exception as e:
        print(e)
        return redirect('vendor')
    return render(request, 'vendor/order_detail.html', context)


def order_delete(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order.delete()
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))
        ordered_food.delete()

        return redirect("vendor_my_orders")
    except Exception as e:
        print(e)
        return redirect('vendor')


def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']
    context = {
       'orders': orders,
        'orders_count': orders.count(),
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,

    }
    return render(request, 'vendor/my_orders.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def table_builder(request):
    vendor = get_vendor(request)
    print(vendor)
    tables = Table.objects.filter(vendor=vendor).order_by('created_at')
    print(tables)
    context = {
        'tables': tables,
    }
    return render(request, 'vendor/table_builder.html', context)


def vendor_tables(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    tables = Table.objects.filter(vendor=vendor)
    tables_available = Table.objects.filter(vendor=vendor, status=1)
    print("tables_available", tables_available)
    tables_unavailable = Table.objects.filter(vendor=vendor, status=0)
    print("tables_unavailable", tables_unavailable)
    # tables = Table.objects.filter(vendor=vendor).prefetch_related(
    #     Prefetch(
    #         'fooditems',
    #         queryset=FoodItem.objects.filter(is_available=True)
    #     )
    # )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    # Check current day's opening hours
    today_date = date.today()
    today = today_date.isoweekday()

    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    # if request.user.is_authenticated:
    #     cart_items = Cart.objects.filter(user=request.user)
    # else:
    #     cart_items = None
    context = {
        'vendor': vendor,
        'tables': tables,
        'tables_available': tables_available,
        'tables_unavailable': tables_unavailable,
        # 'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours
    }
    return render(request, 'marketplace/vendor_tables.html', context)


def vendor_table_detail(request, table_number):
    # order_number = request.GET.get('order_number')
    # transaction_id = request.GET.get('trans_id')
    # print("order_number", order_number)
    # print("transaction_id", transaction_id)
    # print("fbehgdvfgcbdghdg")

    try:
        table = Table.objects.get(number=table_number, is_ordered=True)
        print(table)
        ordered_food = OrderedFood.objects.filter(order=table)
        print("Je suis rentré dans le try")

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        # tax_data = json.loads(order.tax_data)
        # print(tax_data)

        # Update the order model
        # order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the Cart items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            # ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity  # total amount
            ordered_food.save()

        # Send order confirmation email to the customer
        mail_subject = 'Thank you for ordering with us.'
        mail_template = 'orders/order_confirmation_email.html'

        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity)
        # tax_data = json.loads(order.tax_data)
        arguments = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
            'ordered_food': ordered_food,
            'domain': get_current_site(request),
            'customer_subtotal': customer_subtotal,
            # 'tax_data': tax_data,
        }
        send_notification(mail_subject, mail_template, arguments)

        # Send order received email to the vendor
        mail_subject = 'You have received a new order'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)

                ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.fooditem.vendor)
                print(ordered_food_to_vendor)
                # print('to_emails=>', to_emails)

                arguments = {
                    'order': order,
                    'to_email': i.fooditem.vendor.user.email,
                    'ordered_food_to_vendor': ordered_food_to_vendor,
                    'vendor_subtotal': order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'],
                    'tax_data': order_total_by_vendor(order, i.fooditem.vendor.id)['tax_dict'],
                    'vendor_grand_total': order_total_by_vendor(order, i.fooditem.vendor.id)['grand_total'],
                }
                send_notification(mail_subject, mail_template, arguments)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            # 'tax_data': tax_data
        }
        print("je suis redirigé")

        # old_payments(request)

        return render(request, 'orders/order_complete.html', context)
    except Exception as e:
        print('Je coince ici')
        print(e)
        return redirect('home')


@login_required(login_url='login')
def place_order_table(request, pk):
    print(pk)
    table = Table.objects.get(pk=pk)
    vendor = Vendor.objects.get(pk=table.vendor.id)
    print(vendor)
    customer = UserProfile.objects.get(user=request.user)
    print(customer.address)
    print(customer.state)
    print(customer.country)
    print(request.user.phone_number)


    vendors_ids = []


    # Calcul des taxes et du total pour chaque vendeur
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    form = OrderForm()

    # if request.method == 'POST':
    #     form = OrderForm(request.POST)
    #     formReservation = ReservationForm(request.POST)
    #     if form.is_valid():
    #         print("je suis venu ici")
    #         reservation = Reservations()
    #         reservation.customer = customer
    #         reservation.restaurant = vendor
    #         reservation.table = table
    #         reservation.reservation_date = formReservation.cleaned_data['reservation_date']
    #
    #         # return render(request, 'orders/table_place_order.html', context)
    #     else:
    #         print(form.errors)
    # else:
    #     form = OrderForm()
    formReservation = ReservationForm()
        # print(form.errors)

    print(table)

    context = {
        'form': formReservation,
        'table': table,
        # 'cart_items': cart_items,
        "customer": customer,
    }
    print('hbvfhvbgfv fgvt')

    return render(request, 'orders/table_place_order.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_table(request):
    if request.method == 'POST':
        form = TableForm(request.POST, request.FILES)
        if form.is_valid():
            table = form.save(commit=False)
            table.vendor = get_vendor(request)
            table.save()  # when the category object is saved the the category id will be generated
            table.number = generate_order_number(table.id)
            table.save()
            messages.success(request, 'Table added successfully!')
            return redirect('table_builder')
        else:
            print(form.errors)
    else:
        form = TableForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_table.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_table(request, pk=None):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        form = TableForm(request.POST, request.FILES, instance=table)
        if form.is_valid():
            # category_name = form.cleaned_data['category_name']
            table = form.save(commit=False)
            table.vendor = get_vendor(request)
            # category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Table updated successfully!')
            return redirect('table_builder')
        else:
            print(form.errors)
    else:
        form = TableForm(instance=table)
    context = {
        'form': form,
        'table': table,
    }
    return render(request,'vendor/edit_table.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_table(request, pk=None):
    table = get_object_or_404(Table, pk=pk)
    table.delete()
    messages.success(request, 'Table has been deleted successfully!')
    return redirect('table_builder')


def my_reservations(request):
    vendor = Vendor.objects.get(user=request.user)
    reservations = Reservations.objects.filter(restaurant=vendor.id, is_ordered=True).order_by('-created_at')
    current_month = datetime.now().month
    current_month_orders = reservations.filter(restaurant=vendor.id, created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        # current_month_revenue += i.get_total_by_vendor()['grand_total']
        current_month_revenue += i.total
    total_revenue = 0
    for i in reservations:
        total_revenue += i.total
        # total_revenue += i.get_total_by_vendor()['grand_total']
    context = {
        'reservations': reservations,
        'reservations_count': reservations.count(),
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,

    }
    return render(request, 'vendor/my_reservations.html', context)
        