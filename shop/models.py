from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta
from taggit.managers import TaggableManager
from autoslug import AutoSlugField

from django.utils.text import slugify
# Create your models here.

from django.db.models.fields.files import ImageField, ImageFieldFile
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

class ResizedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        # Open the uploaded image
        img = Image.open(content)

        # Resize the image to fit within the maximum size while maintaining the aspect ratio
        max_size = (800, 800)  # You can adjust this size as needed
        img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Use LANCZOS resampling filter

        # Save the resized image to a BytesIO object with reduced quality, in WebP format
        img_io = BytesIO()

        # Ensure the file format is WebP
        webp_name = f"{name.rsplit('.', 1)[0]}.webp"  # Change file extension to .webp
        img.save(img_io, format="WEBP", quality=100)  # Save in WebP format with the desired quality
        img_io.seek(0)

        # Create a SimpleUploadedFile with the resized image data
        content = SimpleUploadedFile(webp_name, img_io.read(), content_type="image/webp")

        # Save the resized image using the parent class method
        super().save(webp_name, content, save)

class ResizedImageField(ImageField):
    attr_class = ResizedImageFieldFile


class AnonymousUser(models.Model):
    session_key = models.CharField(max_length=40, unique=True)

    def __str__(self) -> str:
        st = self.session_key
        new_string = st.replace('.', '')
        return new_string


class CollectionSet(models.Model):
    name=models.CharField(max_length=100)
    hero=models.BooleanField(default=False)
    image=ResizedImageField(upload_to='collectionset/',blank=True,null=True)
    mobile_image = ResizedImageField(upload_to="collectionset/",blank=True,null=True)
    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url
    @property
    def mobileimageURL(self):
        try:
            url=self.mobile_image.url
        except:
            url=''
        return url
    def __str__(self):
        return str(f'{self.name}')



class ProductCategory(models.Model):
    name=models.CharField(max_length=100)
    collection=models.ManyToManyField(CollectionSet)
    image=ResizedImageField(upload_to='category/',blank=True,null=True)
    is_popular = models.BooleanField(default=False)

    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url
    @property
    def sizeChartURL(self):
        try:
            url=self.size_chart.url
        except:
            url=''
        return url
    def __str__(self):
        return str(f'{self.name} ')

class UserProfile(models.Model):
    
    user=models.OneToOneField(User,on_delete=models.SET_NULL,null=True)
    join_at=models.DateTimeField(default=now,blank=True)

    def __str__(self):
        return str(self.user.username)

class AddOnProduct(models.Model):
    name=models.CharField(max_length=100)
    price=models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=10,null=True,blank=True)


    def __str__(self) -> str:
        return f'{self.name}-{self.size}-{self.price}tk'

class Product(models.Model):
    name=models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name',unique=True,null=True,default=None)

    product_code=models.CharField(max_length=100,null=True,blank=True)
    add_on_product=models.ManyToManyField(AddOnProduct,blank=True)
    add_on_product2=models.ManyToManyField(AddOnProduct,related_name='ad_on_2',blank=True)
    add_on_product3=models.ManyToManyField(AddOnProduct,related_name="ad_on_3",blank=True)
    description=models.TextField(null=True,blank=True)
    
    desc = models.TextField(null=True,blank=True)
    price = models.IntegerField(default=0)
    unstitched_price = models.PositiveIntegerField(default=0)
    discount_percent=models.IntegerField(default=0)
    main_price = models.IntegerField(default=0)
    discount=models.BooleanField(default=True,null=True,blank=False)
    productCategory = models.ManyToManyField(ProductCategory)
    collectionset = models.ForeignKey(CollectionSet,on_delete=models.SET_NULL,null=True,blank=True)
    image=ResizedImageField(upload_to='product-image/',blank=True,null=True)
    image2=ResizedImageField(upload_to='product-image/',blank=True,null=True)
    image3=ResizedImageField(upload_to='product-image/',blank=True,null=True)
    image4=ResizedImageField(upload_to='product-image/',blank=True,null=True)
    arrive_at=models.DateTimeField(default=now,blank=True)
    new_arrival=models.BooleanField(default=False,blank=True)
    tags = TaggableManager()
    in_stock=models.BooleanField(default=True,blank=True)
    ratting = models.FloatField(default=0)
    def __str__(self):
        return str(f'{self.name} ')

    
    def update_price(self):
        if self.discount:
            discount = float(self.price * (self.discount_percent / 100))
            discounted_price = float(self.price - discount)
            self.main_price=self.price

            self.discount=False
            self.price = discounted_price
            self.save()
            return discounted_price
        else:
            discount = float(self.main_price * (self.discount_percent / 100))
            discounted_price = self.price - discount

            return discount+self.price


    # def save(self, *args, **kwargs):
    #     calculated_price = self.update_price()  
    #     super().save(*args, **kwargs)


    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url
    @property
    def imageURL2(self):
        try:
            url=self.image2.url
        except:
            url=''
        return url
    @property
    def imageURL3(self):
        try:
            url=self.image3.url
        except:
            url=''
        return url
    @property
    def imageURL4(self):
        try:
            url=self.image4.url
        except:
            url=''
        return url
    
    def average_rating(self):
        reviews = Review.objects.filter(product=self)
        if reviews.exists():
            avg = sum([review.ratting for review in reviews]) / len(reviews)
            self.ratting = round(avg, 1)
            try:
                self.save()  # Save the updated rating
                print(f"Updated rating for {self.name}: {self.ratting}")
            except Exception as e:
                print(f"Failed to save Product {self.id}: {e}")
            return round(avg, 1)
        return 0
    def total_reviews(self):
        reviews = Review.objects.filter(product=self)
        if reviews.exists():
            return len(reviews)
        return 0
    
    
    
    @classmethod
    def get_new_arrivals(cls):
        # Get the current time and subtract 15 days from it
        threshold_date = timezone.now() - timedelta(days=30)
        # Filter products that arrived within the last 15 days
        return cls.objects.filter(arrive_at__gte=threshold_date)

class Order(models.Model):
    STATUS_CHOICES = [
        ('not_confirm','not_confirm'),
        ('Confirmed','Confirmed'),
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    LOCATION_CHOICES = [
        ('inside_dhaka', 'Inside Dhaka'),
        ('outside_dhaka', 'Outside Dhaka'),
    ]

    user=models.ForeignKey(UserProfile,on_delete=models.SET_NULL,null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    items = models.ManyToManyField('Product', through='OrderItem')
    created_at=models.DateTimeField(default=now,blank=True)
    complete=models.BooleanField(default=False,blank=True)
    order_id=models.CharField(max_length=20,null=True,blank=True)
    coupon=models.BooleanField(default=False,null=True,blank=True)
    coupon_percentange=models.PositiveIntegerField(default=0,null=True,blank=True)
    cancel_reason=models.TextField(null=True,blank=True)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, null=True, blank=True)
    totalbill= models.PositiveIntegerField(default=0)
    delivary_charge = models.PositiveIntegerField(default=False)
    # action_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    status_changed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)


    def __str__(self):
        return str(f'{self.user} order')
    @property
    def get_total(self):
        order_items = OrderItem.objects.filter(order=self)
        total = sum(item.item_total for item in order_items)
        if self.coupon:
            total-=total*(self.coupon_percentange/100)

        return int(total)

       


    @property
    def total(self):
        order_items = OrderItem.objects.filter(order=self)
        total = sum(item.item_total for item in order_items)

        return int(total)

    @property
    def total_items(self):
        order_items = OrderItem.objects.filter(order=self)
        total = sum(item.quantity for item in order_items)
        return total 



class OrderItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField(default=0)
    add_on_product= models.ManyToManyField(AddOnProduct)
    order = models.ForeignKey(Order, related_name='order_items',null=True, on_delete=models.CASCADE)
    size=models.CharField(max_length=10,blank=True,null=True)
    is_stitched = models.BooleanField(default=True)
    @property
    def item_total(self):
        add_on = self.add_on_product.all()
        total_add_on = sum(add_pro.price for add_pro in add_on)
        if  self.is_stitched:
            total=self.product.price*self.quantity
        else:  
            total=self.product.unstitched_price*self.quantity
        return total+(total_add_on*self.quantity)

class ShippingAddress(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    address=models.TextField()
    address_note=models.CharField(max_length=100)
    phon=models.CharField(max_length=20)
    email=models.CharField(max_length=100)
    timestamp=models.DateTimeField(default=now,blank=True)
    
    seen_by = models.ManyToManyField(UserProfile, related_name="seen_orders", blank=True)


    def __str__(self):
        return str(f'{self.phon}  ')


class Review(models.Model):
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE, null=True, blank=True)
    user_name = models.CharField(max_length=50,null=True)
    content= models.TextField()
    image=ResizedImageField(upload_to='product-review/',blank=True,null=True)

    ratting = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
    )
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    at_time = models.DateTimeField(default=now, blank=True)

    
    def __str__(self):
        return str(f'{self.user} - {self.user_name} {self.product.name}' )
    


class Cuppon(models.Model):
    cuppon_name=models.CharField(max_length=10)
    percent=models.PositiveIntegerField(default=0)
    min_order= models.PositiveIntegerField(default=0)
    

class PageVisit(models.Model):
    url = models.CharField(max_length=255)
    view_name = models.CharField(max_length=255)
    session_address = models.CharField(max_length=255, null=True, blank=True)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.view_name} ({self.url}) - {self.count} visits"
    