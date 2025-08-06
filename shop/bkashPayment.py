import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Sandbox credentials (store these securely in production)
BKASH_APP_KEY = "0vWQuCRGiUX7EPVjQDr0EUAYtc"
BKASH_APP_SECRET = "jcUNPBgbcqEDedNKdvE4G1cAK7D3hCjmJccNPZZBq96QIxxwAMEx"
BKASH_USERNAME = "01770618567"
BKASH_PASSWORD = "D7DaC<*E*eG"
BASE_URL = "https://tokenized.sandbox.bka.sh/v1.2.0-beta"


def get_token():
    url = f"{BASE_URL}/tokenized/checkout/token/grant"
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
    data = response.json()
    if data.get("statusMessage") == "Successful":
        return data
    return None


def create_agreement(request):
    token_data = get_token()
    if not token_data:
        return JsonResponse({"error": "Failed to get token"}, status=400)

    id_token = token_data['id_token']
    headers = {
        "Accept": "application/json",
        "Authorization": id_token,
        "X-App-Key": BKASH_APP_KEY,
    }

    body = {
        "mode": "0000",
        "callbackURL": "http://127.0.0.1:8000/bkash/create-payment/",  # Local callback
        "payerReference": "01619777282",
        "amount": "25",
        "currency": "BDT",
        "intent": "sale"
    }

    response = requests.post(f"{BASE_URL}/tokenized/checkout/create", headers=headers, json=body)
    data = response.json()

    request.session['token'] = id_token
    request.session['paymentID'] = data.get('paymentID')

    return redirect(data.get('bkashURL'))


# @csrf_exempt
def execute_agreement(request):
    paymentID = request.session.get('paymentID')
    id_token = request.session.get('token')

    if not paymentID or not id_token:
        return JsonResponse({"error": "Session expired or missing data"}, status=400)

    url = f"{BASE_URL}/tokenized/checkout/execute"
    headers = {
        "Accept": "application/json",
        "Authorization": id_token,
        "X-App-Key": BKASH_APP_KEY,
    }
    body = {
        "paymentID": paymentID
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    agreementID = data.get("agreementID")
    if not agreementID:
        return JsonResponse({"error": "Failed to execute agreement"}, status=400)

    return agreementID


def create_payment(request):
    
    id_token = request.session.get('token')
    agreementID = execute_agreement(request)
    
    if not id_token or not agreementID:
        return JsonResponse({"error": "Missing token or agreementID"}, status=400)

    headers = {
        "Accept": "application/json",
        "Authorization": id_token,
        "X-App-Key": BKASH_APP_KEY,
    }

    body = {
        "mode": "0001",
        "payerReference": "01619777282",
        "callbackURL": "http://127.0.0.1:8000/bkash/execute-payment/",
        "agreementID": agreementID,
        "amount": "25",
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": "Inv0124"
    }

    response = requests.post(f"{BASE_URL}/tokenized/checkout/create", headers=headers, json=body)
    data = response.json()

    request.session['paymentID'] = data.get('paymentID')

    return redirect(data.get('bkashURL'))


# @csrf_exempt
def execute_payment(request):
    paymentID = request.session.get('paymentID')
    id_token = request.session.get('token')

    if not paymentID or not id_token:
        return JsonResponse({"error": "Missing paymentID or token"}, status=400)

    url = f"{BASE_URL}/tokenized/checkout/payment/execute"
    headers = {
        "Accept": "application/json",
        "Authorization": id_token,
        "X-App-Key": BKASH_APP_KEY,
    }
    body = {
        "paymentID": paymentID
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    return JsonResponse(data)
