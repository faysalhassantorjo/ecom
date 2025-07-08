from django.shortcuts import render,redirect
from .models import Product,OrderItem,Order,UserProfile,AnonymousUser,ProductCategory,ShippingAddress,Review,CollectionSet,Cuppon,PageVisit
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
    # ,'faysalhassantorjo8@gmail.com'
    recipient_list = [customr_email]
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

# def check_user(request):
#     request.session.save()
#     session_key = request.session.session_key
    
#     if request.user.is_authenticated:
#         userProfile= UserProfile.objects.get(user = request.user)
#         return userProfile
    
#     try:
#         userProfile = UserProfile.objects.get(user__username = session_key)
#     except:
#         userProfile = None
#     return userProfile

# def get_user(request):
#     user =None
#     if request.user.is_authenticated:
#         user=request.user
#         userprofile, created = UserProfile.objects.get_or_create(user=user)
#     else:
#         u=create_anonymous_user(request)
#         user,c=User.objects.get_or_create(username=u)
#         userprofile, created = UserProfile.objects.get_or_create(user=user,is_anonymous = True)
#     return userprofile
from django.contrib.auth import authenticate, login

def user_login(request):
    if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                order_id = request.session.get('order',None)
                session_id = get_session_id(request)
                order_items=None
                if order_id:
                    session_order = Order.objects.filter(sesssion_id = session_id).first()
                    order_items = session_order.order_items.all()
                    print('order items are : ', order_items)
                else:
                    print('no order is FOund')
                    
                login(request, user)
                if order_items:
                    user =UserProfile.objects.get(user=request.user)
                    prev_order,c = Order.objects.get_or_create(user=user,complete=False)
                    
                    for item in order_items:
                        item.order = prev_order
                        item.save()
                    session_order.delete()
                    
                next_url = request.GET.get('next') or '/'
                print('next url', next_url)
                return redirect(next_url)
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
    print('visit stats2')
    




    return render(request, 'shop/visit_stats.html')

from django.db.models import Q
def home(request):


    if request.method == "GET":
        data= request.GET.get('data', None)
        print('data is: ',data)
        if data is not None:
            products = Product.objects.filter(
                Q(name__icontains = data) |
                Q(tags__name__icontains = data)
            )
            print(products)
        
            return render ( request, 'shop/shop.html', {'products':set(products)})
    CACHE_TIMEOUT = 60 * 20

    # Cache keys
    cache_keys = {
        'top_rated_products': 'top_rated_products',
        'hero_collections': 'hero_collections',
        'collection_sets': 'collection_sets',
        'discount_products': 'discount_products',
        'all_categories': 'all_categories',
        'new_arrivals': 'new_arrivals',
        'popular_category': 'popular_category',
    }

    def get_cached_data(key, query_func, timeout=CACHE_TIMEOUT):
        data = cache.get(key)
        if data is None:
            data = query_func() 
            cache.set(key, data, timeout)
            print(f'Query occurred for {key}')
        
        return data

    top_rated_products = get_cached_data(
        cache_keys['top_rated_products'],
        lambda: Product.objects.filter(ratting__gt=2).order_by('?')
    )

    popular_category = get_cached_data(
        cache_keys['popular_category'],
        lambda: ProductCategory.objects.filter(is_popular=True)
    )

    hero_collections = get_cached_data(
        cache_keys['hero_collections'],
        lambda: CollectionSet.objects.filter(hero=True).order_by('-id'),
        timeout=60*60  # Cache for 60 minutes
    )

    collection_sets = get_cached_data(
        cache_keys['collection_sets'],
        lambda: CollectionSet.objects.filter(hero=False)
    )

    discount_products = get_cached_data(
        cache_keys['discount_products'],
        lambda: Product.objects.filter(discount_percent__gt=5).order_by('?')[:8]
    )

    all_categories = get_cached_data(
        cache_keys['all_categories'],
        lambda: ProductCategory.objects.all().order_by('?')
    )

    new_arrivals = get_cached_data(
        cache_keys['new_arrivals'],
        lambda: Product.get_new_arrivals().order_by('?')[:8]
    )
    
    print('discount products:',discount_products)
    context={
        'top_rated_product':top_rated_products,
        'heroCollections': hero_collections,
        'collectionsets':collection_sets,
        'discount_products':discount_products,
        'all_categories':all_categories[:8],
        'new_arrivals':new_arrivals,
        'popular_category':popular_category
    }


    try:
        order =[]
        userProfile=None
        if request.user.is_authenticated:
            try:
                userProfile,created = UserProfile.objects.get_or_create(user  = request.user)
                
                order=Order.objects.get(user=userProfile,complete=False)
            except:
                order=[]
        else:
            session_id = get_session_id(request)
            order= Order.objects.filter(sesssion_id = session_id, complete=False).first()
            
        items=OrderItem.objects.filter(order=order)
        
        context.update({'order':order,'items':items,'userProfile':userProfile})
    except Exception as e:
        print(e)



    return render(request,'shop/nav.html',context)

import json
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

def get_session_id(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    return session_key


@csrf_exempt
def create_order_item(request):

    if request.method == 'POST':
        size = request.POST.get('size', None)
        customization_note = request.POST.get('customization_note', None)
        actionanddata = request.POST.get('action', None)
        cart = request.POST.get('from', None)
        
        is_istiched = request.POST.get('unstitched', None) 
        item_id = request.POST.get('item_id', None) 
        
        if is_istiched is not None:
            if is_istiched.lower() == 'true':
                is_istiched = True
            else:
                is_istiched = False
        else:
            is_istiched = True

      

        splited_data=actionanddata.split()
        productId=(splited_data[1])
        action=splited_data[0]

        product = Product.objects.get(slug=productId)
        
        if request.user.is_authenticated:
            userprofile = UserProfile.objects.get(user=request.user)
        
            order, c = Order.objects.get_or_create(user=userprofile, complete=False)
        
        else:
            session_id = get_session_id(request)
            order,c = Order.objects.get_or_create(sesssion_id=session_id, complete=False)

        if item_id:
            orderItem=OrderItem.objects.get(id=item_id)
        else:
            orderItem, _ = OrderItem.objects.get_or_create(
                    product=product,
                    order=order,
                    size=size,
                    is_stitched = is_istiched,
                    customization_note=customization_note 
            )
        

        if action == 'add':
            orderItem.quantity += 1
            print('order item added')
            messages.success(request, 'Product added to cart successfully.')
        elif action == 'remove':
            orderItem.quantity -= 1
            print('product removed')
        elif action == 'delete':
            orderItem.quantity = 0
        print('is product is istiched?',is_istiched)
        orderItem.size = size
        orderItem.save()
        order.status = 'not_confirm'
        order.totalbill=order.total
            
        if orderItem.quantity <= 0:
            print(orderItem.product.name)
            orderItem.delete()
            print('product deletedhjfdashjhdj')
            
        order.save()

        if cart:
            return redirect('cart')
        
        request.session['order'] = str(order.id)
        
        return JsonResponse({'status': 'success', 'message': 'Item added to cart'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

from .form import ShippingAddressForm
def createOrder(request):


    return JsonResponse("Order done", safe=False)

def cart(request):
    # userProfile = check_user(request)
    order = None
    
    if request.user.is_authenticated:
        try:
            u = UserProfile.objects.get(user=request.user)
            order = Order.objects.get(
                user = u,
                complete = False
            )
        except Exception as e:
            order = None
            print('error',e)
    else:
        try:
            session_id = get_session_id(request)
            order = Order.objects.get(sesssion_id =session_id,complete =False )
        except Exception as e:
            order = None
            print('error',e)
    
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
        
        print("orders: ", order)
        context = {
            'order': order,
            'saves': saves
        }
    except Exception as e:
        print(e)
        return render(request, 'shop/404.html')
        
    return render(request, 'shop/cart.html', context)

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
import time
def checkout(request):
    order = None

    if request.user.is_authenticated:
        u = UserProfile.objects.get(user=request.user)
        order = Order.objects.filter(user=u, complete=False).first()
    else:
        session_id = get_session_id(request)
        order = Order.objects.filter(sesssion_id=session_id, complete=False).first()

    if not order:
        return render(request, 'shop/404.html', {'e': "You don't have any order. Add products to your cart."})

    if order.total_items == 0:
        return render(request, 'shop/404.html', {'e': "Your cart is empty. Add products to your cart."})

    subtotal = order.get_total + order.delivary_charge
    items = OrderItem.objects.filter(order=order)
    total = items.count()

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.order = order
            shipping_address.save()
            order.complete = True
            order.status = "Pending"
            order.totalbill = subtotal
            order.save()
            request.session['order'] = 'None'
            return redirect('order_success', pk=shipping_address.id)
    else:
        form = ShippingAddressForm()

    context = {
        'total': total,
        'items': items,
        'order': order,
        'form': form,
        'subtotal': subtotal
    }

    return render(request, 'shop/checkout.html', context)

def order_success(request,pk):
    data=ShippingAddress.objects.get(id=pk)
    total = data.order.get_total+data.order.delivary_charge

    context={
        'shippingaddress':data,
        'total':total
    }
    return render(request,'shop/orderSuccess.html',context)
def shop_grid(request,pk):
    
    context={}
    
    try:

        userProfile = check_user(request)
        order =[]
        if userProfile:
            try:
                order=Order.objects.get(user=userProfile,complete=False)
            except:
                order=[]
        
        collection=CollectionSet.objects.get(id=pk)
        
        if collection.hero:
            
            
            products = Product.objects.filter(collectionset = collection)
          
            context.update({'products':products})
        else:
            cache_key = f"collection_category{pk}"
                    
            categories =cache.get(cache_key)
            
        
            if categories is None:
                
                categories=collection.productcategory_set.all()
                
                cache.set(cache_key,categories,timeout=60*20)

                print('categories',categories)

            context.update({'categories':categories})

        context.update({

                'x':True,
                'collection':collection,
                'order':order
            })
        return render(request,'shop/shop2.html',context)
    except Exception as e:
        print(e)
        return render(request,'shop/404.html')

from django.urls import reverse

def go_to_admin_panel(request):
    return redirect(reverse('admin:index'))

@cache_page(60 * 60) 
def products(request,pk):

    cat=ProductCategory.objects.get(id=pk)
    
    cache_key = f'product_category_{pk}'
    products = cache.get(cache_key) 
    if products is None:
        
        products=cat.product_set.all().order_by('?')
        cache.set(cache_key,products,timeout=60*30)
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
        
        cache_key = f'product_{slug}'
        related_cache_key = f'product_related_{slug}'

        product = cache.get(cache_key)
        related_data = cache.get(related_cache_key)
  
        

        if product is None:
            product = Product.objects.get(slug=slug)
            cache.set(cache_key, product, timeout=60*20)  

        if related_data is None:
            reviews = Review.objects.filter(product=product)
            # add_on_product = product.add_on_product.all()
            # add_on_product2 = product.add_on_product2.all()
            # add_on_product3 = product.add_on_product3.all()
            product_categories = product.productCategory.all()
            relatePro = Product.objects.filter(tags__in=product.tags.all()).exclude(id=product.id).distinct().order_by('?')[:4]

            # Cache related data
            related_data = {
                'reviews': reviews,
                # 'add_on_product': add_on_product,
                # 'add_on_product2': add_on_product2,
                # 'add_on_product3': add_on_product3,
                'product_categories': product_categories,
                'relatePro': relatePro,
                'tags': product.tags.all(),
            }
            cache.set(related_cache_key, related_data, timeout=60*20)  # Cache for 20 minutes
            print('Related data query occurred')

        # Retrieve cached related data
        reviews = related_data['reviews']
        # add_on_product = related_data['add_on_product']
        # add_on_product2 = related_data['add_on_product2']
        # add_on_product3 = related_data['add_on_product3']
        product_categories = related_data['product_categories']
        relatePro = related_data['relatePro']
        tags = related_data['tags']

        # Form for reviews
        form = WriteReview()

        star_count = product.average_rating

    
        product = Product.objects.get(slug=slug)
        
        context = {
            'product': product,
            'form': form,
            'reviews': reviews,
            'star_count': star_count,
            'relatedProduct': relatePro[:6],
            # 'add_on_product': add_on_product,
            # 'add_on_product2': add_on_product2,
            # 'add_on_product3': add_on_product3,
            'product_categories': product_categories,
            'tags': tags,
        }

        hero_collections = cache.get('hero_collections')
        collection_sets = cache.get('collection_sets')
        if hero_collections and collection_sets:
            context.update(
                {
                   'collectionsets':collection_sets,
                   'heroCollections':hero_collections
                }
            )

        try:
           
            if request.user.is_authenticated:
                upro = UserProfile.objects.get(user=request.user)
                order = Order.objects.filter(user_id = upro, complete = False).first()
                print("user",request.user)
                print('userprofile',request.user.userprofile)
            else:
                session_id = get_session_id(request)
                order = Order.objects.filter(sesssion_id = session_id,complete=False).first()
            items=order.order_items.all()
            
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
from django.db import transaction
from datetime import timedelta
@admin_only
def viewOrder(request):
    two_weeks_ago = timezone.now() - timedelta(weeks=2)

    shippingAddress=ShippingAddress.objects.filter(order__status = "Pending",).order_by('-timestamp')
    confrimed_order = ShippingAddress.objects.filter(order__status = "Confirmed", order__created_at__gte=two_weeks_ago).order_by('-timestamp')
    cancelled_order = ShippingAddress.objects.filter(order__status = "Cancelled", order__created_at__gte=two_weeks_ago).order_by('-timestamp')
    print(confrimed_order)
   

    context={
       'shippingAddresss': shippingAddress,
       'confirmed_order': confrimed_order,
       'canceled_order': cancelled_order,
    }
    return render(request,'shop/viewOrder2.html',context)

def order_status(request):
    
    if request.method == 'POST':
        order_id = request.POST.get('order-id')
        status = request.POST.get('status')
        order=Order.objects.get(id=order_id)
        
        order.status = status
        
        shippingAddress=ShippingAddress.objects.get(order = order)
        order.status_changed_by = request.user
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

    
@admin_only
def product_add(request):
    print('add product')
    form2=AddCategory(request.POST, request.FILES)
    form3=AddCollection(request.POST, request.FILES)
    if request.method == 'POST':
        form=AddProduct(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Product Added Successfully!")
            return redirect('product_add')
        else:
            messages.error(request,"Some Error Occured!")
            
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
            messages.success(request,"Category Added Successfully!")
            return redirect('product_add')
        else:
            messages.error(request,"Some Error Occured!")
            return redirect('product_add')
        


from django.http import HttpResponse
def addCollection(request):
    if request.method == 'POST':
        form = AddCollection(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_add')
        else:
            return HttpResponse("Form is not valid. Please check your inputs.")


@admin_only
def edit_product(request,slug):
    product = Product.objects.get(slug=slug)

    if request.method == 'POST':
        form=AddProduct(request.POST,request.FILES,instance=product)

        if form.is_valid():
            form.save()
            return redirect('shop_details',slug=slug)
    else:
        form=AddProduct(instance=product)

    context={
        'form':form,
        'product':product
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