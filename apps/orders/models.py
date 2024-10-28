from django.db import models
from apps.accounts.models import User
from apps.menu.models import FoodItem
from apps.vendor.models import Vendor
import simplejson as json
import string
import random

request_object = ''

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPAl'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.transaction_id
    
    
class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50, default="", null=True)
    last_name = models.CharField(max_length=50, default="", null=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    # country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    # pin_code = models.CharField(max_length=10)
    total = models.FloatField()
    # tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type':{'tax_percentage':'tax_amount'}}", null=True)
    total_data = models.JSONField(blank=True, null=True)
    # total_tax = models.FloatField()
    # payment_method = models.CharField(max_length=25)
    status = models.CharField(choices=STATUS, max_length=15, default='New')
    is_ordered = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)  # Nouveau champ pour la confirmation du paiement
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def save(self, *args, **kwargs):
    #     res = ''.join(random.choices(string.ascii_letters,
    #                                  k=7))  # initializing size of string
    #     self.order_number=res
    #     super(Order, self).save(*args, **kwargs)


    @property
    def name(self):
        return f'{self.user.full_name}'
    
    def order_placed_to(self):
        return ", ".join([str(i) for i in self.vendors.all()])

    def get_total_by_vendor(self):
        # Code existant pour calculer le total par vendeur
        vendor = Vendor.objects.get(user=request_object.user)
        subtotal = 0
        tax = 0
        tax_dict = {}

        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id))
            print("data", data)

            for key, val in data.items():
                print("1")
                subtotal += float(key)
                print("2")
                val = val.replace("'", '"')
                print("3")
                val = json.loads(val)
                print(type(val))
                print("4")
                print(tax_dict)

                # Ensure `val` is a dictionary before proceeding
                if isinstance(val, dict):
                    for i in val:
                        print("6")
                        if isinstance(val[i], dict):  # Check if val[i] is a dictionary
                            for j in val[i]:
                                print("7")
                                tax += float(val[i][j])
                                print("8")
                        else:
                            print(f"Warning: val[i] is not a dictionary, got {type(val[i])}")
                else:
                    print(f"Warning: val is not a dictionary, got {type(val)}")

        grand_total = float(subtotal) + float(tax)
        context = {
            'subtotal': subtotal,
            'tax_dict': tax_dict,
            'grand_total': grand_total,
        }

        return context

    def __str__(self):
        return self.order_number



class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.fooditem.food_title



