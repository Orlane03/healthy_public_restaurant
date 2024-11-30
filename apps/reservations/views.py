from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponse, JsonResponse
from apps.accounts.models import UserProfile
from .forms import ReservationForm
from .models import Vendor, Table, Reservations
from django.contrib import messages
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from ..accounts.utils import send_notification
from ..orders.utils import generate_order_number


@login_required(login_url='login')
def confirmation_reservation(request):
    if request.method == 'POST':
        print("dhnfbvhbdfhvbgb")
        table_id = request.POST.get('table_id')
        table = Table.objects.get(pk=table_id)
        vendor = Vendor.objects.get(pk=table.vendor.id)
        print("order_number", table_id)
        customer = UserProfile.objects.get(user=request.user)
        grand_total = table.price

        formReservation = ReservationForm(request.POST)
        if formReservation.is_valid():
            print("je suis venu ici")
            reservation = Reservations()
            reservation.total = grand_total
            reservation.customer = customer
            reservation.restaurant = vendor
            reservation.table = table
            print(reservation.reservation_date)
            reservation.reservation_date = formReservation.cleaned_data['reservation_date']

            reservation.is_confirmed = True  # Confirmer directement la commande
            reservation.is_ordered = True  # Confirmer directement la commande
            reservation.save()

            # Génération du numéro de commande
            reservation.number = generate_order_number(reservation.id)
            reservation.save()

            # Send order confirmation email to the customer
            mail_subject = 'Thank you for reservation with us.'
            mail_template = 'reservations/reservation_confirmation_email.html'

            # ordered_food = OrderedFood.objects.filter(order=order)
            # customer_subtotal = 0
            # for item in ordered_food:
            #     print("14")
            #     customer_subtotal += (item.price * item.quantity)
            #     print("15")
            # tax_data = json.loads(order.tax_data)
            arguments = {
                'user': request.user,
                'reservation': reservation,
                'table': table,
                'to_email': request.user.email,
                # 'ordered_food': ordered_food,
                'domain': get_current_site(request),
                # 'tax_data': tax_data,
            }
            send_notification(mail_subject, mail_template, arguments)

            # Send order received email to the vendor
            mail_subject = 'You have received a new reservation'
            mail_template = 'reservations/new_reservation_received.html'
            # to_emails = []
            # for i in cart_items:
        # if i.fooditem.vendor.user.email not in to_emails:
        #     to_emails.append(vendor.user.email)

            # ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.fooditem.vendor)
            # print(ordered_food_to_vendor)
            # print('to_emails=>', to_emails)

            # print(order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'])
            print('debug')

            arguments = {
                'reservation': reservation,
                'table': table,
                'to_email': vendor.user.email,
                'domain': get_current_site(request),
                # 'ordered_food_to_vendor': ordered_food_to_vendor,
                # 'vendor_subtotal': order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'],
                # 'tax_data': order_total_by_vendor(order, i.fooditem.vendor.id)['tax_dict'],
                # 'vendor_grand_total': order_total_by_vendor(order, i.fooditem.vendor.id)['grand_total'],
            }
            send_notification(mail_subject, mail_template, arguments)

            context = {
                "reservation": reservation
            }

            # return render(request, 'reservations/reservations_complete.html', context)
            return redirect(
                reverse(
                "reservation_complete",
                kwargs= {
                    "reservation_number": reservation.number
                }
            ))
        else:
            print(formReservation.errors)
    else:
        pass
            # return render(request, 'orders/table_place_order.html', context)

        # payment_method = request.POST.get('payment_method')
        # print("payment_method", payment_method)

        # Récupérer la commande et mettre à jour le statut de paiement
        # try:
        #     order = Order.objects.get(order_number=order_number, user=request.user)
        #     order.is_ordered = True  # Confirme le paiement
        #     # order.payment_method = payment_method
        #     order.save()
        #
        #     print("Je veux rediligert")
        #     # Rediriger vers la page de confirmation de commande
        #     return redirect(
        #         reverse(
        #             "order_complete",
        #             kwargs={"order_number": order_number},
        #         )
        #     )
        #     # Assurez-vous que 'order_complete' est bien configurée pour afficher la confirmation
        # except Order.DoesNotExist:
        #     print("hfbcgvgfdsvdfvbgdfvbg")
        #     return redirect('checkout')  # Redirection en cas d'échec

    return HttpResponse('Invalid request method.', status=400)


def reservation_complete(request, reservation_number):
    print(reservation_number)
    reservation = Reservations.objects.get(number=reservation_number)
    table = Table.objects.get(pk=reservation.table.id)
    vendor = Vendor.objects.get(pk=table.vendor.id)
    context = {
        "reservation": reservation,
        "table": table
    }
    return render(request, 'reservations/reservations_complete.html', context)


@login_required(login_url='login')
def c_reservations(request):
    # Récupérer les commandes de l'utilisateur connecté
    user = UserProfile.objects.get(user=request.user)
    reservations = Reservations.objects.filter(customer=user.id).order_by('-created_at')
    reservations_count = reservations.count()

    # Contexte passé au template
    context = {
        'reservations': reservations,
        "reservations_count": reservations_count,
    }
    return render(request, 'reservations/c_my_reservations.html', context)


def reservation_detail(request, number):
    print("h d vjbbhhbfvhd")
    print(number)
    try:
        reservation = Reservations.objects.get(number=number, is_ordered=True)
        print('jbfhvbjghvg')
        table = Table.objects.get(pk=reservation.table.id)
        # ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))
        # vendor = Vendor.objects.get(user=request.user)

        context = {
            'reservation': reservation,
            'table': table,
            'grand_total': reservation.total,
        }
        return render(request, 'reservations/reservation_detail.html', context)

    except Exception as e:
        print(e)
        return redirect('vendor')


