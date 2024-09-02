from django.shortcuts import render,redirect
from .models import Product,OrderItem,Order,UserProfile,AnonymousUser,ProductCategory,ShippingAddress,Review,CollectionSet,Cuppon,AddOnProduct,PageVisit
import json
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from .form import PriceSortForm,WriteReview,OrderStatus,AddProduct,AddCategory,AddCollection,LoginForm,OrderCancel

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout,authenticate
from django.core.cache import cache
from django.views.decorators.cache import cache_page


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.conf import settings

def send_html_email(shippingAddress):
    subject = f'Order Being Processed #{shippingAddress.order.order_id}'
    html_message = render_to_string('shop/mail.html', {'shippingaddress': shippingAddress})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    # 'Jannatulferdospia77@gmail.com'
    customr_email = shippingAddress.email
    recipient_list = [customr_email,'faysalhassantorjo8@gmail.com','Jannatulferdospia77@gmail.com']
    print('customer mail ', customr_email)
    email = EmailMessage(
        subject,
        html_message,
        from_email,
        recipient_list,
    )
    email.content_subtype = 'html'  # Important to send HTML content
    email.send()
    print('Email send done')

def send_confermation_mail(shippingAddress):
    subject = f'Order Confirmed #{shippingAddress.order.order_id}'
    html_message = render_to_string('shop/order-comfrim-mail.html', {'shippingaddress': shippingAddress})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    customr_email = shippingAddress.email
    recipient_list = [customr_email,'faysalhassantorjo8@gmail.com']
    print('customer mail ', customr_email)
    email = EmailMessage(
        subject,
        html_message,
        from_email,
        recipient_list,
    )
    email.content_subtype = 'html' 
    email.send()
    print('Email send done')

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip

def get_cart_total_items(request):
    userProfile = check_user(request)
    order =[]
    if userProfile:
        try:
            order=Order.objects.get(user=userProfile,complete=False)
        except:
            order=[]
    return order

def create_anonymous_user(request):
    request.session.save()
    # session_key = get_ip(request)
    session_key = request.session.session_key
    print(session_key)
    anonymous_user,c = AnonymousUser.objects.get_or_create(session_key=session_key)
    return anonymous_user

def check_user(request):
    request.session.save()
    session_key = request.session.session_key
    
    if request.user.is_authenticated:
        userProfile= UserProfile.objects.get(user = request.user)
        return userProfile
    
    try:
        userProfile = UserProfile.objects.get(user__username = session_key)
    except:
        userProfile = None
    return userProfile

def get_user(request):
    user =None
    if request.user.is_authenticated:
        user=request.user
    else:
        u=create_anonymous_user(request)
        user,c=User.objects.get_or_create(username=u)
    try:
        userprofile, created = UserProfile.objects.get_or_create(user=user)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return userprofile
from django.contrib.auth import authenticate, login

def user_login(request):
    if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to homepage or dashboard after login
            else:
                messages.error(request, 'Invalid username or password')

    return render(request, 'shop/login.html')

def logoutV(request):
    logout(request)
    return redirect('home')

from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        # Validate passwords
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'shop/register.html')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'shop/register.html')

        # Create the user
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        messages.success(request, f"Account created for {username}")
        login(request, user)
        return redirect('home') 
    else: return render(request, 'shop/register.html')
    return render(request, 'shop/register.html')

# def cart_items(request):
   
#     userprofile=get_user(request)
#     try:
#         order=Order.objects.get(user=userprofile,complete=False)
#         items=OrderItem.objects.filter(order=order)
    
#         return items
#     except:
#         return []
from collections import Counter

def visit_stats(request):
    # Get all page visits
    visits = PageVisit.objects.all()

    # Count total visits
    total_visits = visits.count()

    # Count visits by URL and convert to a dictionary
    url_visit_counts = dict(Counter(visits.values_list('url', flat=True)))

    # Prepare data for the graph
    urls = list(url_visit_counts.keys())
    visit_counts = list(url_visit_counts.values())

    context = {
        'total_visits': total_visits,
        'url_visit_counts': url_visit_counts,
        'urls': urls,
        'visit_counts': visit_counts,
    }

    return render(request, 'shop/visit_stats.html', context)
def home(request):
    
    # send_html_email()
    cache_keys = {
        'top_rated_products': 'top_rated_products',
        'hero_collections': 'hero_collections',
        'collection_sets': 'collection_sets',
        'discount_products': 'discount_products',
        'all_categories': 'all_categories',
        'new_arrival_products': 'new_arrival_products',
    }


    # Get data from cache
    top_rated_products = cache.get(cache_keys['top_rated_products'])
    hero_collections = cache.get(cache_keys['hero_collections'])
    collection_sets = cache.get(cache_keys['collection_sets'])
    discount_products = cache.get(cache_keys['discount_products'])
    all_categories = cache.get(cache_keys['all_categories'])
    new_arrival_products = cache.get(cache_keys['new_arrival_products'])

    # If not in cache, query the database and store in cache
    if not top_rated_products:
        top_rated_products = Product.objects.filter(ratting__gt=2).order_by('?')
        cache.set(cache_keys['top_rated_products'], top_rated_products, timeout=60*20)  
        print('Query occured 1')

    if not hero_collections:
        hero_collections = CollectionSet.objects.filter(hero=True)
        cache.set(cache_keys['hero_collections'], hero_collections, timeout=60*20)  # Cache for 15 minutes
        print('Query occured 2')

    if not collection_sets:
        collection_sets = CollectionSet.objects.filter(hero=False)
        cache.set(cache_keys['collection_sets'], collection_sets, timeout=60*20)  # Cache for 15 minutes
        print('Query occured 3')

    if not discount_products:
        discount_products = Product.objects.filter(discount_percent__gt=5)
        cache.set(cache_keys['discount_products'], discount_products, timeout=60*20)  # Cache for 15 minutes
        print('Query occured 4')

    if not all_categories:
        all_categories = ProductCategory.objects.all().order_by('?')
        cache.set(cache_keys['all_categories'], all_categories, timeout=60*20)  # Cache for 15 minutes
        print('Query occured 5')

    if not new_arrival_products:
        new_arrival_products = Product.objects.filter(new_arrival=True).order_by('?')
        cache.set(cache_keys['new_arrival_products'], new_arrival_products, timeout=60*20)  # Cache for 15 minutes
        print('Query occured 6')


    # for product in products:
    #     rating=product.average_rating()
    #     time_frame = timezone.now() - product.arrive_at
    #     if  time_frame.days <= 10:
    #         product.new_arrival=True
    #         product.save()
    #     else:
    #         product.new_arrival=False
    #         product.save()

    context={
        'top_rated_product':top_rated_products,
        'new_arrival_products':new_arrival_products[:8],
        'heroCollections':hero_collections,
        'collectionsets':collection_sets,
        'discount_product':discount_products,
        'all_categories':all_categories[:10],
    }

    user=request.user
    if user.is_authenticated:
        userProfile,created = UserProfile.objects.get_or_create(user  = user)
        context.update({'userProfile':userProfile})

    try:
        userProfile = check_user(request)
        order =[]
        if userProfile:
            try:
                order=Order.objects.get(user=userProfile,complete=False)
            except:
                order=[]
        items=OrderItem.objects.filter(order=order)
        
        context.update({'order':order,'items':items})
    except Exception as e:
        print(e)



    return render(request,'shop/nav.html',context)

import json
from django.http import JsonResponse
from django.contrib import messages

def create_order_item(request):

    if request.method == 'POST':
        size = request.POST.get('size', None)
        actionanddata = request.POST.get('action', None)
        cart = request.POST.get('from', None)
        add_product=request.POST.get('add_on_product',None)
        add_product2=request.POST.get('add_on_product2',None)
        add_product3=request.POST.get('add_on_product3',None)
        
        is_istiched = request.POST.get('unstitched', None)  # Retrieve 'unstitched' from POST request
        print("fasghasdfadag: ",is_istiched)
        if is_istiched is not None:
            if is_istiched.lower() == 'true':
                is_istiched = True
            else:
                is_istiched = False
        else:
            is_istiched = True


            
        print('hello this is : ',is_istiched)
        if add_product or add_product2 or add_product3:
            print(add_product)
            try: 
                if add_product:
                    add_on_product = AddOnProduct.objects.get(id=int(add_product))
            
            except:
                print('No add on get 1')

            try: 

                add_on_product2 = AddOnProduct.objects.get(id=int(add_product2))

            except:
                print('No add on get 2')
            try: 


                add_on_product3= AddOnProduct.objects.get(id=int(add_product3))
            except:
                print('No add on get 3')


        userprofile = get_user(request)

        splited_data=actionanddata.split()
        productId=(splited_data[1])
        action=splited_data[0]

        product = Product.objects.get(slug=productId)
        order, c = Order.objects.get_or_create(user=userprofile, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(product=product, order=order, size=size,is_stitched = is_istiched)
        
        if add_product or add_product2 or add_product3:
            try: 
                orderItem.add_on_product.add(add_on_product)

            except:
                print("No add on selected 1")
            
            try:
                orderItem.add_on_product.add(add_on_product2)
            except:
                print("No add on selected 2")
            
            try: 
                orderItem.add_on_product.add(add_on_product3)
            except:
                print("No add on selected 3")

        if action == 'add':
            orderItem.quantity += 1
            print('order item added')
            messages.success(request, 'Product added to cart successfully.')
        elif action == 'remove':
            orderItem.quantity -= 1
            print('product removed')
        elif action == 'delete':
            orderItem.quantity = 0
            print('product deleted')
        print('is product is istiched?',is_istiched)
        orderItem.size = size
        orderItem.save()
        order.status = 'not_confirm'
        order.totalbill=order.total
            
        if orderItem.quantity == 0:
            orderItem.delete()
        order.save()
        

        if cart:
            return redirect('cart')

        return redirect('shop_details',slug=productId)

from .form import ShippingAddressForm
def createOrder(request):

    
    

    return JsonResponse("Order done", safe=False)

def cart(request):
    userProfile = check_user(request)
    order = None
    
    if userProfile:
        try:
            order = Order.objects.get(user=userProfile, complete=False)
        except Order.DoesNotExist:
            order = None
    
    try:
        coupons = Cuppon.objects.all()

        if request.method == 'POST':
            q = request.POST['q']
            print('coupon', q)

            for c in coupons:
                if c.coupon_name == q and order and not order.coupon:
                    if order.get_total >= c.min_order:
                        order.coupon = True
                        order.coupon_percentage = c.percent
                        order.save()

        print('My get_total', order.get_total if order else 0)
        print('My total bill:', order.totalbill if order else 0)
        
        saves = 0
        if order and order.coupon:
            saves = abs(order.total - order.get_total)
        
        print('get_order')
        
    
        context = {
            'order': order,
            'userProfile': userProfile,
            'saves': saves
        }
    except Exception as e:
        print(e)
        return render(request, 'shop/404.html')
        
    return render(request, 'shop/shopping-cart.html', context)

def location_choice(request,pk):
    order=Order.objects.get(id=pk)
    location = request.POST.get('location')
    
    if location in ['outside_dhaka', 'inside_dhaka']:
        order.location = location
        
        if location == 'outside_dhaka':
            order.delivary_charge = 150
        elif location == 'inside_dhaka':
            order.delivary_charge = 80

        order.save()
        return redirect('checkout')
    context={
        'order':order
    }
    return render(request,'shop/location_choice.html',context)

def profile(request,pk):
    user=UserProfile.objects.get(id=pk)
    orders=Order.objects.filter(user=user,complete=True).order_by('-created_at')
    print(user)
    print(orders)

    
        
    context={
        'orders':orders,
        'userProfile':user

    }
    return render(request,'shop/profile.html',context)

def order_cancel(request,pk):
    # order=Order.objects.get(id=pk)
    # order.status='Cancelled'
    # order.save()
    order=Order.objects.get(id=pk)
    if request.method == 'POST':
        form = OrderCancel(request.POST,instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.status='Cancelled' 
            order.save()          
            return redirect('/')
    else:
        form = OrderCancel(instance=order)
    context={
        'form':form
    }
    return render(request,'shop/orderStatus.html',context)

def checkout(request):
    userProfile = check_user(request)
    order =[]
    if userProfile:
        try:
            order=Order.objects.get(user=userProfile,complete=False)
        except:
            order=[]
    try:
        if order.total_items == 0:
            return render(request,'shop/404.html',{'e':"Your Cart Have 0 product. Add Product in your Cart."})
            
    except Exception:
        return render(request,'shop/404.html',{'e':"You Don't Have any Order. Add Product in your Cart."})
        
    
    subtotal = order.get_total+order.delivary_charge

    items=OrderItem.objects.filter(order=order)
    total=items.count()

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)  
            shipping_address.order=order
            shipping_address.save()
            print("shipping Address: ",shipping_address.id)
            order_id = int(datetime.datetime.now().timestamp())
            order.order_id=order_id
            order.complete=True
            order.status="Pending"
            order.totalbill=subtotal
            order.save()
            send_html_email(shipping_address)
            return redirect('order_success',pk=shipping_address.id)

    else:
        form = ShippingAddressForm()

    

    context={
        'total':total,
        'items':items,
        'order':order,
        'form':form,
        'userProfile':userProfile,
        'subtotal':subtotal
    }
 
    return render(request,'shop/checkout.html',context)
def order_success(request,pk):
    data=ShippingAddress.objects.get(id=pk)
    total = data.order.get_total+data.order.delivary_charge

    context={
        'data':data,
        'total':total
    }
    return render(request,'shop/orderSuccess.html',context)
def shop_grid(request,pk):
    
    try:

        userProfile = check_user(request)
        order =[]
        if userProfile:
            try:
                order=Order.objects.get(user=userProfile,complete=False)
            except:
                order=[]
        
        collection=CollectionSet.objects.get(id=pk)
        
        cache_key = f"collection_category{pk}"
                
        categories = cache.get(cache_key)
        
        if categories is None:
            
            categories=collection.productcategory_set.all()
            
            cache.set(cache_key,categories,timeout=60*20)

            print('categories',categories)


        context={
                # 'products':products,
                'categories':categories,
                'x':True,
                'collection':collection,
                'order':order
            }
        return render(request,'shop/shop2.html',context)
    except Exception as e:
        print(e)
        return render(request,'shop/404.html')

from django.urls import reverse

def go_to_admin_panel(request):
    return redirect(reverse('admin:index'))

# @cache_page(60 * 20) 
def products(request,pk):

    cat=ProductCategory.objects.get(id=pk)
    
    cache_key = f'product_category_{pk}'
    products = cache.get(cache_key) 
    if products is None:
        
        products=cat.product_set.all().order_by('?')
        cache.set(cache_key,products,timeout=60*20)
        print('product query occured')


    total_products = products.count()

   

    context={
        'products':products,
        'categories':cat,
        'total_products':total_products,
    }
    return render(request,'shop/shop.html',context) 

from django.db.models import Q
def shop_details(request,slug):
    try:
        product=Product.objects.get(slug=slug)
        product.average_rating
        form=WriteReview()
        reviews=Review.objects.filter(product=product)

        add_on_product = product.add_on_product.all()
        add_on_product2 = product.add_on_product2.all()
        add_on_product3 = product.add_on_product3.all()


        product_categories=product.productCategory.all()
  

        star_count = product.average_rating

        lis=product.tags.all()
        
        
        try:
            visit_count = PageVisit.objects.filter(url=request.path).first().count
        except:
            visit_count =0
            
        absolute_image_url = request.build_absolute_uri(product.imageURL)

        relatePro = Product.objects.filter(tags__in=product.tags.all()).exclude(id=product.id).distinct().order_by('?')[:4]

        can_review = True

        # if request.user.is_authenticated:
        #     user = get_user(request)
        #     order,c=Order.objects.get_or_create(user=user,complete=False)
        #     # user_profile = UserProfile.objects.get(user=user)
        #     user_orders = Order.objects.filter(user=user)

        #     for order in user_orders:
        #         order_items = OrderItem.objects.filter(order=order)
        #         for order_item in order_items:
        #             if order_item.product == product:
        #                 can_review = True
        #                 break
        #         if can_review:
        #             break

        cate = product.productCategory.earliest('id')

        print(cate)

        context={
            'product':product,
            'form':form,
            'reviews':reviews,
            'star_count':star_count,
            'relatedProduct':relatePro[:6],
            'add_on_product':add_on_product,
            'add_on_product2':add_on_product2,
            'add_on_product3':add_on_product3,
            'product_categories':product_categories,
            'tags':lis,
            'can_review':can_review,
            'order':get_cart_total_items(request),
            'visit_count':visit_count,
            'absolute_image_url': absolute_image_url,
        }
        user=request.user
        if user.is_authenticated:
            userProfile,created = UserProfile.objects.get_or_create(user  = user)
            context.update({'userProfile':userProfile})

        try:
            userProfile = check_user(request)
            order =[]
            if userProfile:
                try:
                    order=Order.objects.get(user=userProfile,complete=False)
                except:
                    order=[]
            items=OrderItem.objects.filter(order=order)
            
            context.update({'order':order,'items':items})
        except Exception as e:
            print(e)

        return render(request,'shop/shop-details2.html',context)
    except Exception as e:
        print(e)
        return render(request,'shop/404.html',context={
            'e':e
        })

from .decorator import admin_only
@admin_only
def viewOrder(request):

    shippingAddress=ShippingAddress.objects.filter(order__status = "Pending").order_by('-timestamp')
    confrimed_order = ShippingAddress.objects.filter(order__status = "Confirmed").order_by('-timestamp')
    cancelled_order = ShippingAddress.objects.filter(order__status = "Cancelled").order_by('-timestamp')
    
    userProfile=get_user(request)

    context={
       'shippingAddresss': shippingAddress,
       'confirmed_order': confrimed_order,
       'canceled_order': cancelled_order,
       'userProfile':userProfile
    }
    return render(request,'shop/viewOrder2.html',context)

def order_status(request):
    
    if request.method == 'POST':
        order_id = request.POST.get('order-id')
        status = request.POST.get('status')
        order=Order.objects.get(id=order_id)
        
        order.status = status
        
        shippingAddress=ShippingAddress.objects.get(order = order)
   
        order.save()
        
        if order.status == "Confirmed":
            send_confermation_mail(shippingAddress)
            print("------------")
            print("Email sent done")
            
        return redirect('viewOrder')

    return HttpResponse('somthing worng')

from django.contrib.auth.decorators import login_required
from PIL import Image as PILImage
from io import BytesIO

# @login_required(login_url='login')
def writeReview(request, slug):
    product = Product.objects.get(slug=slug)

    if request.method == 'POST':
        # Get user from request or POST data
   
        user = request.POST.get('user_name')
        
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        
        # Ensure all fields are present before creating the review
        if user and rating and content:
            review = Review.objects.create(
                product=product,
                user_name=user, 
                ratting=rating,
                content=content
            )
            
            if request.user.is_authenticated:
                user = request.user
                userprofile =UserProfile.objects.get(user = user)
                review.user = userprofile
                review.save()
            
            return redirect('shop_details', slug=slug)
        else:
            # Handle the case where some fields are missing
            print("Missing review fields.")
            return redirect('shop_details', slug=slug)
    
    return redirect('shop_details', slug=slug)        

    
    
def product_add(request):
    form2=AddCategory(request.POST, request.FILES)
    form3=AddCollection(request.POST, request.FILES)
    if request.method == 'POST':
        form=AddProduct(request.POST,request.FILES)

        if form.is_valid():
            form.save()
            return redirect('product_add')
    else:
        form=AddProduct()

    context={
        'form':form,
        'form2':form2,
        'form3':form3,
    }
    return render(request,'shop/addProduct.html',context)

from django.http import HttpResponse

def addCategory(request):
    if request.method == 'POST':
        form=AddCategory(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_add')
        else:
            return HttpResponse("Form is not valid. Please check your inputs.")


from django.http import HttpResponse
def addCollection(request):
    if request.method == 'POST':
        form = AddCollection(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_add')
        else:
            return HttpResponse("Form is not valid. Please check your inputs.")



def edit_product(request,pk,pk2):
    product=Product.objects.get(id=pk)

    if request.method == 'POST':
        form=AddProduct(request.POST,request.FILES,instance=product)

        if form.is_valid():
            form.save()
            return redirect('products',pk=pk2)
    else:
        form=AddProduct(instance=product)

    context={
        'form':form
    }
    return render(request,'shop/editProduct.html',context)

def delete_product(request,pk,pk2):
    product=Product.objects.get(id=pk)
    
    product.delete()

    return redirect('products', pk=pk2)

def confirm_page(request,pk,pk2):
    context={
        'product_id':pk,
        'return_id':pk2,
    }
    return render(request,'shop/confirm_page.html',context)

def custom_404_view(request,exception):
    return render(request, 'shop/404.html', status=404)