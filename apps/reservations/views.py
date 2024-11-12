from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponse, JsonResponse
from apps.accounts.models import UserProfile
from .models import Vendor, Table
from django.contrib import messages
from django.urls import reverse

@login_required(login_url='login')
def confirmation_reservation(request):
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
