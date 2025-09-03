import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Payment, CompletedOrder, ShippingAddress
from django.contrib import messages
from django.db import transaction
from django.core.cache import cache


from decouple import config

BKASH_APP_KEY = config("BKASH_APP_KEY")
BKASH_APP_SECRET = config("BKASH_APP_SECRET")
BKASH_USERNAME = config("BKASH_USERNAME")
BKASH_PASSWORD = config("BKASH_PASSWORD")
BASE_URL = config("BASE_URL")

# sandbox
# BKASH_APP_KEY = "0vWQuCRGiUX7EPVjQDr0EUAYtc"
# BKASH_APP_SECRET = "jcUNPBgbcqEDedNKdvE4G1cAK7D3hCjmJccNPZZBq96QIxxwAMEx"
# BKASH_USERNAME = "01770618567"
# BKASH_PASSWORD = "D7DaC<*E*eG"
# BASE_URL = "https://tokenized.sandbox.bka.sh/v1.2.0-beta"


def get_token():
    url = f"{BASE_URL}/tokenized/checkout/token/grant"
    id_token = cache.get('id_token')
    
    if id_token: 
        return {'id_token':id_token}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "username": BKASH_USERNAME,
        "password": BKASH_PASSWORD,
    }
    body = {
        "app_key": BKASH_APP_KEY,
        "app_secret": BKASH_APP_SECRET
    }
    response = requests.post(url, headers=headers, json=body)
    res = response.json()
    
    if "id_token" in res:
        cache.set('id_token',res.get('id_token'),timeout=1800)
    
    return response.json()


def create_payment(request,name,order_id,amount=150):
    token_data = get_token()
    id_token = token_data.get("id_token")

    if not id_token:
        return JsonResponse({"error": "Could not fetch token"}, status=400)
    
    order = Order.objects.filter(id = order_id).first()
    
    if not order:
        messages.error(request, "Order is not found, Some error occured!")
        return redirect('checkout')

    headers = {
        "Accept": "application/json",
        "Authorization": id_token,
        "X-App-Key": BKASH_APP_KEY,
    }
    

    body = {
        "mode": "0011",   # For checkout
        "payerReference": name,
        "callbackURL": "https://longgfashion.onrender.com/bkash/execute-payment/",
        # "callbackURL": "http://127.0.0.1:8000/bkash/execute-payment/",
        "amount": amount,
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": f'{order_id}'
    }

    response = requests.post(f"{BASE_URL}/tokenized/checkout/create", headers=headers, json=body)
    data = response.json()
    
    request.session['paymentID'] = data.get("paymentID")
    
    try:
        
        return redirect(data.get("bkashURL"))
    
    except :
        return JsonResponse(data)


def execute_payment(request):
    id_token = cache.get('id_token')
    paymentID = request.session.get("paymentID")

    if not paymentID or not id_token:
        messages.error(request, "Payment faild, Some error occurred!")
        return redirect('checkout')

    headers = {
        "Accept": "application/json",
        "Authorization": id_token,
        "X-App-Key": BKASH_APP_KEY,
    }

    body = {"paymentID": paymentID}

    response = requests.post(f"{BASE_URL}/tokenized/checkout/execute", headers=headers, json=body)
    
    response_data = response.json()
    order_id = response_data.get("merchantInvoiceNumber")
    
    if response_data.get("transactionStatus") == "Completed":
        payment = Payment.objects.create(
                    payment_id=response_data.get("paymentID"),
                    transaction_status="completed",
                    method="bkash",
                    amount=response_data.get("amount", 0)
                )
        try:    
            with transaction.atomic():
                order = Order.objects.filter(id=order_id).first()
                if not order:
                    messages.error(request, "Payment completed but somehow order is not completed! please contact with us with your transaction id.")
                    return redirect('checkout')
                order.complete = True
                order.paid = response_data.get("amount", 0)
                order.save()
                    
                shipping_data =request.session['shipping_address']
                             
                shipping = ShippingAddress.objects.create(
                    **shipping_data
                )
                    
                completed_order = CompletedOrder.objects.create(
                    order=order,
                    payment=payment,
                    user = request.user if request.user.is_authenticated else None,
                    shipping_address = shipping
                )
                    
                    
                request.session.pop('order_id', None)
                request.session.pop('shipping_address_id', None)
                request.session.pop('shipping_address', None)
                
                messages.success(request, "Payment successful and order completed.")
                return redirect('order_success', pk=order.id)
       
        except Exception as e:
            messages.error(request, "Payment completed but somehow order is not completed! please contact with us with your transaction id.")
            return redirect('checkout')
    
    elif response_data.get("transactionStatus") == "Failed":
        messages.error(request, "Transaction Faild")
        return redirect('checkout')
    
    elif response_data.get("statusCode") == "2056":
        
        messages.error(request,"Invalid Payment State")
        return redirect('checkout')
        
    
    messages.error(request,"Payment failed. Please try again.")  
        
    return redirect('checkout')
        
      