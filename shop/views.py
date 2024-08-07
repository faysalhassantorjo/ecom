from django.shortcuts import render,redirect
from .models import Product,OrderItem,Order,UserProfile,AnonymousUser,ProductCategory,ShippingAddress,Review,CollectionSet,Cuppon,AddOnProduct
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

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            userprofile,created = UserProfile.objects.get_or_create(user =user)
            return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'shop/login.html', {'form': form})

def logoutV(request):
    logout(request)
    return redirect('home')

from django.contrib.auth.forms import UserCreationForm

def register(request):
    try:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                authenticated_user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password1'])

                if authenticated_user is not None:
                    UserProfile.objects.create(user=user)
                    auth_login(request, authenticated_user)
                    return redirect("home")
        else:
            form = UserCreationForm()
    except Exception as e:
        return render(request,'shop/404.html')

    return render(request, 'shop/register.html', {'form': form})


# def cart_items(request):
   
#     userprofile=get_user(request)
#     try:
#         order=Order.objects.get(user=userprofile,complete=False)
#         items=OrderItem.objects.filter(order=order)
    
#         return items
#     except:
#         return []

    


def home(request):
    
    
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
        top_rated_products = Product.objects.filter(_ratting__gt=2)
        cache.set(cache_keys['top_rated_products'], top_rated_products, timeout=60*1)  
        print('Query occured 1')

    if not hero_collections:
        hero_collections = CollectionSet.objects.filter(hero=True)
        cache.set(cache_keys['hero_collections'], hero_collections, timeout=60*1)  # Cache for 15 minutes
        print('Query occured 2')

    if not collection_sets:
        collection_sets = CollectionSet.objects.filter(hero=False)
        cache.set(cache_keys['collection_sets'], collection_sets, timeout=60*1)  # Cache for 15 minutes
        print('Query occured 3')

    if not discount_products:
        discount_products = Product.objects.filter(discount_percent__gt=5)
        cache.set(cache_keys['discount_products'], discount_products, timeout=60*1)  # Cache for 15 minutes
        print('Query occured 4')

    if not all_categories:
        all_categories = ProductCategory.objects.all().order_by('?')
        cache.set(cache_keys['all_categories'], all_categories, timeout=60*1)  # Cache for 15 minutes
        print('Query occured 5')

    if not new_arrival_products:
        new_arrival_products = Product.objects.filter(new_arrival=True).order_by('?')
        cache.set(cache_keys['new_arrival_products'], new_arrival_products, timeout=60*1)  # Cache for 15 minutes
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
        'all_categories':all_categories[:10]
    }

    user=request.user
    if user.is_authenticated:
        userProfile = UserProfile.objects.get(user  = user)
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
            messages.success(request, 'Product added to cart successfully.')
        elif action == 'remove':
            orderItem.quantity -= 1
        elif action == 'delete':
            orderItem.quantity = 0
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
            order.delivary_charge = 120
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
            
            cache.set(cache_key,categories,timeout=60)

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

def products(request,pk):

    cat=ProductCategory.objects.get(id=pk)
    
    cache_key = f'product_category_{pk}'
    products = cache.get(cache_key) 
    if products is None:
        
        products=cat.product_set.all().order_by('?')
        cache.set(cache_key,products,timeout=60*1)
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

        form=WriteReview()



        reviews=Review.objects.filter(product=product)

        add_on_product = product.add_on_product.all()
        add_on_product2 = product.add_on_product2.all()
        add_on_product3 = product.add_on_product3.all()


        product_categories=product.productCategory.all()
  

        star_count = product.average_rating

        lis=product.tags.all()
        
        

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
            'order':get_cart_total_items(request)
        }
        
        return render(request,'shop/shop-details.html',context)
    except Exception as e:
        print(e)
        return render(request,'shop/404.html',context={
            'e':e
        })

from .decorator import admin_only
@admin_only
def viewOrder(request):

    shippingAddress=ShippingAddress.objects.all().order_by('-timestamp')
    
    userProfile=get_user(request)

    context={
       'shippingAddress': shippingAddress,
       'userProfile':userProfile
    }
    return render(request,'shop/viewOrder.html',context)

def order_status(request,pk):
    
    order=Order.objects.get(id=pk)
    if request.method == 'POST':
        form = OrderStatus(request.POST,instance=order)
        if form.is_valid():
            order = form.save()
            
            return redirect('viewOrder')
    else:
        form = OrderStatus(instance=order)
    context={
        'form':form
    }
    return render(request,'shop/orderStatus.html',context)

from django.contrib.auth.decorators import login_required
from PIL import Image as PILImage
from io import BytesIO

@login_required(login_url='login')
def writeReview(request,slug):
    product = Product.objects.get(slug=slug)
    userProfile=get_user(request)

    if request.method == 'POST':
        form=WriteReview(request.POST,request.FILES)
        if form.is_valid():
                ratting = form.cleaned_data['ratting']
                content = form.cleaned_data['content']
                original_image = form.cleaned_data['image']
                image = Review(ratting=ratting, content=content)
                image.user=userProfile
                image.product = product
                image.image = original_image
                image.save()  # Save the model instance
                
                # return redirect('success_url')  # Redirect to success page
                return redirect('shop_details', slug=slug)
    else: return redirect('shop_details', slug=slug)
        

    
    
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