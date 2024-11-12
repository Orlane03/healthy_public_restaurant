from apps.accounts.models import UserProfile
from apps.vendor.models import Vendor, Table
from django.db import models

STATUS_CHOICE = (
    (0, 'CREATED'),
    (1, 'PENDING'),
    (2, "CANCELLED"),
    (3, "DONE")
)


class Reservations(models.Model):
    customer = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name="customer_reservation")
    restaurant =  models.ForeignKey(Vendor, on_delete=models.DO_NOTHING, related_name="restaurant_reservation")
    table = models.ForeignKey(Table, on_delete=models.DO_NOTHING, related_name="table_reservation")
    nmbreofpeople = models.PositiveIntegerField(default=1)
    reservation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICE, default=0, blank=False, null=False)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservation"

    def __unicode__(self):
        return self.customer.full_name

