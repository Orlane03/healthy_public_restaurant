from django.utils.timezone import now
from django import forms
from django.forms import fields
from formset.widgets import DatePicker, DateTimePicker, DateTimeInput
from datetime import timedelta
from bootstrap_datepicker_plus.widgets import DatePickerInput


class ReservationForm(forms.Form):
    reservation_date = fields.DateTimeField(
            widget=DateTimeInput,
        )
        # widget=DatePicker(attrs={
        #     'min': now().isoformat(),
        #     'max': (now() + timedelta(weeks=2)).isoformat(),
        # }),
    # )

    # date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'))

