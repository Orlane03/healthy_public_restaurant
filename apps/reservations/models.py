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
    is_ordered = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    number = models.CharField(max_length=20, default="")
    total = models.FloatField(default=0)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservation"


    @property
    def get_status(self):
        status = ""
        if self.status == 0:
            status = 'CREATED'
        elif self.status == 1:
            status = 'PENDING'
        elif self.status == 2:
            status = "CANCELLED"
        elif self.status == 0:
            status = "DONE"
        return status

    def __unicode__(self):
        return self.customer.full_name

