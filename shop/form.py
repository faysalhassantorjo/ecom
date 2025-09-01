from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from taggit.forms import TagField


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class PriceSortForm(forms.Form):
    PRICE_CHOICES = [
        ('', 'Low To High'),
        ('0-10', '$0 - $10'),
        ('10-20', '$10 - $20'),
    ]

    sort_by_price = forms.ChoiceField(choices=PRICE_CHOICES, required=False)

from django import forms
from .models import ShippingAddress,Review,Order,Product,ProductCategory,CollectionSet

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['name', 'address', 'address_note', 'phon', 'email']

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)

        self.fields['address'].widget = forms.Textarea(attrs={'rows': 4})
        self.fields['email'].required = False
        self.fields['address_note'].required = False


class WriteReview(forms.ModelForm):
    class Meta:
        model=Review
        fields=['ratting','content',]




class AddProduct(forms.ModelForm):
    tags = TagField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Enter tags (comma-separated)'
    }))

    class Meta:
        model = Product
        fields = [
            'name', 'desc', 'price', 'unstitched_price', 'collectionset', 'productCategory', 'image', 'image2', 'image3', 'image4',
            'youtube_video_id', 'new_arrival', 'tags', 'in_stock'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'unstitched_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter unstitched price'}),
            'collectionset': forms.Select(attrs={'class': 'form-select'}),
            'productCategory': forms.SelectMultiple(attrs={'class': 'form-select'}),  # Supports multiple categories
            'youtube_video_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YouTube Video ID'}),
            'new_arrival': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AddCategory(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'collection', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'collection': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AddCollection(forms.ModelForm):
    class Meta:
        model = CollectionSet
        fields = ['name', 'hero', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter collection name'}),
            'hero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hero name'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }