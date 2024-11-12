from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from apps.marketplace.models import Cart
from apps.marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
import simplejson as json
from .utils import generate_order_number, order_total_by_vendor
from apps.accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from apps.menu.models import FoodItem
from apps.marketplace.models import Tax
from django.contrib.sites.shortcuts import get_current_site
# pour la gestion de commande et de paiement
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Order


@login_required(login_url='login')
def confirm_payment(request, order_number):
    # Récupérer la commande en fonction du numéro de commande et de l'utilisateur connecté
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Si le paiement n'est pas encore confirmé, le marquer comme confirmé
    if not order.is_confirmed:
        order.is_confirmed = True
        order.save()
        messages.success(request, 'Le paiement a été confirmé avec succès.')
    else:
        messages.info(request, 'Le paiement de cette commande a déjà été confirmé.')
    
    # Rediriger l'utilisateur vers sa page de commandes
    return redirect('my_orders')


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    vendors_ids = []
    for item in cart_items:
        if item.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(item.fooditem.vendor.id)
            
    # Calcul des taxes et du total pour chaque vendeur
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}
    for item in cart_items:
        fooditem = FoodItem.objects.get(pk=item.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * item.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * item.quantity)
            k[v_id] = subtotal
            
        # Calcul des données de taxe
        # tax_dict = {}
        # for tax in get_tax:
        #     tax_type = tax.tax_type
        #     tax_percentage = tax.tax_percentage
        #     tax_amount = round((tax_percentage * subtotal) / 100, 2)
        #     tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})
        
        # Construction des données totales par vendeur
        total_data.update({fooditem.vendor.id: {str(subtotal): str(subtotal)}})

    print(total_data)

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            # order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            # order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            # order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            # order.total_tax = total_tax
            order.is_confirmed = True  # Confirmer directement la commande
            order.save()  # ID de la commande généré

            # Génération du numéro de commande
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')


@login_required(login_url='login')
def payments(request):
    if request.method == 'POST':
        print("dhnfbvhbdfhvbgb")
        order_number = request.POST.get('order_number')
        print("order_number", order_number)
        payment_method = request.POST.get('payment_method')
        print("payment_method", payment_method)

        
        # Récupérer la commande et mettre à jour le statut de paiement
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            order.is_ordered = True  # Confirme le paiement
            # order.payment_method = payment_method
            order.save()

            print("Je veux rediligert")
            # Rediriger vers la page de confirmation de commande
            return redirect(
              reverse(
                "order_complete",
                kwargs={"order_number": order_number},
              )
            )
            # Assurez-vous que 'order_complete' est bien configurée pour afficher la confirmation
        except Order.DoesNotExist:
            print("hfbcgvgfdsvdfvbgdfvbg")
            return redirect('checkout')  # Redirection en cas d'échec

    return HttpResponse('Invalid request method.', status=400)



@login_required(login_url='login')
def old_payments(request):
    # Check if the request is Ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # Store the payment details in the payment model
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()
        # Update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the Cart items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity # total amount
            ordered_food.save()
        
        # Send order confirmation email to the customer
        mail_subject = 'Thank you for ordering with us.'
        mail_template = 'orders/order_confirmation_email.html'
        
        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
            'ordered_food': ordered_food,
            'domain': get_current_site(request),
            'customer_subtotal': customer_subtotal,
            'tax_data': tax_data,
        }
        send_notification(mail_subject, mail_template, context)
        
        
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
        
                context = {
                    'order': order,
                    'to_email': i.fooditem.vendor.user.email,
                    'ordered_food_to_vendor': ordered_food_to_vendor,
                    'vendor_subtotal': order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'],
                    'tax_data': order_total_by_vendor(order, i.fooditem.vendor.id)['tax_dict'],
                    'vendor_grand_total': order_total_by_vendor(order, i.fooditem.vendor.id)['grand_total'],
                }
                send_notification(mail_subject, mail_template, context)
        
        # Clear the Cart if the payment is success
        # cart_items.delete()
    
        # Return back to Ajax with the status success or failure
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse('Payments view')


def order_complete(request, order_number):
    # order_number = request.GET.get('order_number')
    # transaction_id = request.GET.get('trans_id')
    # print("order_number", order_number)
    # print("transaction_id", transaction_id)
    # print("fbehgdvfgcbdghdg")
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        print(order)
        ordered_food = OrderedFood.objects.filter(order=order)
        print("Je suis rentré dans le try")
        
        subtotal = 0
        print("1")
        for item in ordered_food:
            print("2")
            subtotal += (item.price * item.quantity)
            
        # tax_data = json.loads(order.tax_data)
        # print(tax_data)

        # Update the order model
        # order.payment = payment
        print("3")
        order.is_ordered = True
        print("4")
        order.save()

        # Move the Cart items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        print("4")
        for item in cart_items:
            print("5")
            ordered_food = OrderedFood()
            print("6")
            ordered_food.order = order
            print("7")
            # ordered_food.payment = payment
            ordered_food.user = request.user
            print("8")
            ordered_food.fooditem = item.fooditem
            print("9")
            ordered_food.quantity = item.quantity
            print("10")
            ordered_food.price = item.fooditem.price
            print("11")
            ordered_food.amount = item.fooditem.price * item.quantity  # total amount
            print("12")
            ordered_food.save()

        # Send order confirmation email to the customer
        mail_subject = 'Thank you for ordering with us.'
        mail_template = 'orders/order_confirmation_email.html'

        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        print("13")
        for item in ordered_food:
            print("14")
            customer_subtotal += (item.price * item.quantity)
            print("15")
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

                # print(order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'])
                print('debug')

                arguments = {
                    'order': order,
                    'to_email': i.fooditem.vendor.user.email,
                    'ordered_food_to_vendor': ordered_food_to_vendor,
                    # 'vendor_subtotal': order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'],
                    # 'tax_data': order_total_by_vendor(order, i.fooditem.vendor.id)['tax_dict'],
                    # 'vendor_grand_total': order_total_by_vendor(order, i.fooditem.vendor.id)['grand_total'],
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
        # return redirect('home')


@login_required(login_url='login')
def my_orders(request):
    # Récupérer les commandes de l'utilisateur connecté
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    print('fvdhgfbhvdbghbvjbh')
    
    # Contexte passé au template
    context = {
        'orders': orders,
    }
    
    # Rendre le template `my_orders.html` avec les données des commandes
    return render(request, 'orders/my_orders.html', context)
