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
        fields = ['first_name', 'last_name', 'address', 'address_note', 'phon', 'email']

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)

        self.fields['address'].widget = forms.Textarea(attrs={'rows': 4})
        self.fields['email'].required = False


class WriteReview(forms.ModelForm):
    class Meta:
        model=Review
        fields=['ratting','content',]

class OrderStatus(forms.ModelForm):
    class Meta:
        model=Order
        fields = ['status']
class OrderCancel(forms.ModelForm):
    class Meta:
        model=Order
        fields = ['cancel_reason']

class AddProduct(forms.ModelForm):
    class Meta:
        model = Product
        tags = TagField()
        fields = [
            
            'name',
            'description',
            'price',
            'unstitched_price',
            'productCategory',
            'image',
            'image2',
            'image3',
            'image4',
            'tags',
            'in_stock'         
        ]

class AddCategory(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = [
            'name',
            'collection',
            'image',          
        ]
class AddCollection(forms.ModelForm):
    class Meta:
        model = CollectionSet
        fields = ['name', 'hero', 'image']