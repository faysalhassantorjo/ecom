from django.shortcuts import render,redirect
from .models import Product,OrderItem,Order,UserProfile,AnonymousUser,ProductCategory,ShippingAddress,Review,CollectionSet,Cuppon
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

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip

def create_anonymous_user(request):
    # request.session.save()
    session_key = get_ip(request)
    print(session_key)
    anonymous_user,c = AnonymousUser.objects.get_or_create(session_key=session_key)
    return anonymous_user


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
            return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'shop/login.html', {'form': form})

def logoutV(request):
    logout(request)
    return redirect('home')

from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            authenticated_user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password1'])

            if authenticated_user is not None:
                auth_login(request, authenticated_user)
                return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, 'shop/register.html', {'form': form})


def cart_items(request):
   
    userprofile=get_user(request)
    try:
        order=Order.objects.get(user=userprofile,complete=False)
    except:
        print('you hav no order')

    items=OrderItem.objects.filter(order=order)
    
    return items


def home(request):
    products= Product.objects.all()
    userProfile=get_user(request)
    # print(userProfile)
    top_rated_product=[]

    heroCollections=CollectionSet.objects.filter(hero=True)

    collectionsets=CollectionSet.objects.filter(hero=False)



    for product in products:
        rating=product.average_rating()
        time_frame = timezone.now() - product.arrive_at
        print('time frame',time_frame.days)
        if  time_frame.days <= 7:
            product.new_arrival=True
            product.save()
        else:
            product.new_arrival=False
            product.save()
        if rating>3:
            top_rated_product.append(product)
    
    for i in top_rated_product:
        print(i)

    new_arrival_products = Product.objects.filter(new_arrival=True)

    print(len(new_arrival_products))

    context={
        'products':products,
        'userProfile':userProfile,
        'top_rated_product':top_rated_product,
        'new_arrival_products':new_arrival_products,
        'heroCollections':heroCollections,
        'collectionsets':collectionsets
    }

    

    try:
        order=Order.objects.get(user=userProfile,complete=False)

        items=OrderItem.objects.filter(order=order)
        
        context.update({'order':order,'items':items})
    except Exception as e:
        print(e)



    return render(request,'shop/home.html',context)

def create_order_item(request):
    data = json.loads(request.body)
    print('data',data)
    productId = int(data['productID'])
    action = data['action']
    size = data['selectedSize']
    print(productId)

    userprofile=get_user(request)


    product=Product.objects.get(id=productId)
    order,c=Order.objects.get_or_create(user=userprofile,complete=False)

    orderItem,created=OrderItem.objects.get_or_create(product=product,order=order,size=size)



    if action=='add':
        orderItem.quantity+=1
    elif action=='remove':
        orderItem.quantity-=1
    elif action =='delete':
    
        orderItem.quantity=0


  

    orderItem.size=size
    orderItem.save()
    order.status='not_confirm'
    order.save()
    if orderItem.quantity == 0:
        orderItem.delete()
    return JsonResponse("Item was added", safe=False)
from .form import ShippingAddressForm
def createOrder(request):

    
    

    return JsonResponse("Order done", safe=False)

def cart(request):
    userProfile=get_user(request)
    print(userProfile)

    order,c=Order.objects.get_or_create(user=userProfile,complete=False)

    items=OrderItem.objects.filter(order=order)
    total=items.count()
    coupons=Cuppon.objects.all()

    if request.method=='POST':
        q=request.POST['q']
        print('cuopon ',q)

        for c in coupons:
            if c.cuppon_name==q:
                order.coupon=True
                order.coupon_percentange=c.percent
                order.save()

    saves=order.total - order.get_total

    context={
        'total':total,
        'items':items,
        'order':order,
        'userProfile':userProfile,
        'saves':saves
    }
    return render(request,'shop/shopping-cart.html',context)

def profile(request,pk):
    user=UserProfile.objects.get(id=pk)
    orders=Order.objects.filter(user=user).order_by('-created_at')
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
    userProfile=get_user(request)
    print(userProfile)

    order,c=Order.objects.get_or_create(user=userProfile,complete=False)

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
            order.save()     
            return redirect('order_success',pk=shipping_address.id)

    else:
        form = ShippingAddressForm()

    context={
        'total':total,
        'items':items,
        'order':order,
        'form':form,
        'userProfile':userProfile
    }
 
    return render(request,'shop/checkout.html',context)
def order_success(request,pk):
    data=ShippingAddress.objects.get(id=pk)
    context={
        'data':data
    }
    return render(request,'shop/orderSuccess.html',context)
def shop_grid(request,pk):

    userProfile=get_user(request)

    collection=CollectionSet.objects.get(id=pk)
    categories=collection.productcategory_set.all()

    print('categories',categories)


    context={
        # 'products':products,
        'categories':categories,
        'userProfile':userProfile,
        'x':True
    }
    return render(request,'shop/shop.html',context)

def products(request,pk):
    cat=ProductCategory.objects.get(id=pk)
    print(cat)
    products=cat.product_set.all().order_by('-arrive_at')
    print(products)
    userProfile=get_user(request)

    context={
        'products':products,
        'categories':cat,
        'userProfile':userProfile
    }
    return render(request,'shop/shop.html',context) 

from django.db.models import Q
def shop_details(request,pk):
    product=Product.objects.get(id=pk)
    userProfile=get_user(request)
    print(userProfile)
    form=WriteReview()

    order,c=Order.objects.get_or_create(user=userProfile,complete=False)

    items=OrderItem.objects.filter(order=order)

    reviews=Review.objects.filter(product=product)

    star_count = product.average_rating

    lis=product.tags.all()
    relatePro=[]
    for p in lis:
        a=Product.objects.filter(Q(tags__name__icontains=p.name))
        relatePro.append(a)

    print(relatePro)

    context={
        'product':product,
        'order':order,
        'userProfile':userProfile,
        'form':form,
        'reviews':reviews,
        'star_count':star_count,
        'relatedProduct':relatePro
    }
    return render(request,'shop/shop-details.html',context)
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
@login_required(login_url='login')
def writeReview(request,pk):
    product = Product.objects.get(id=pk)
    userProfile=get_user(request)

    if request.method == 'POST':
        form=WriteReview(request.POST,request.FILES)
        if form.is_valid():
            review=form.save(commit=False)
            review.user=userProfile
            review.product=product
            review.save()
            st='review done'

            return redirect('shop_details', pk=pk)

    
    
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
