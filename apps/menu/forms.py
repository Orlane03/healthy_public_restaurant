from email.mime import image
from django import forms
from apps.accounts.validators import allow_only_images_validator
from .models import Category, FoodItem
from ..vendor.models import Table


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        
        
class FoodItemForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images_validator])
    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'description', "seats",]