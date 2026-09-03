# import os
# import requests
# from datetime import datetime


# class MPesaService:
#     def __init__(self):
#         self.consumer_key = os.getenv('MPESA_CONSUMER_KEY', '')
#         self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', '')
#         self.shortcode = os.getenv('MPESA_SHORTCODE', '')
#         self.passkey = os.getenv('MPESA_PASSKEY', '')
#         self.callback_url = os.getenv('MPESA_CALLBACK_URL', '')
#         self.environment = os.getenv('MPESA_ENV', 'sandbox')

#         if self.environment == 'sandbox':
#             self.base_url = 'https://sandbox.safaricom.co.ke'
#         else:
#             self.base_url = 'https://api.safaricom.co.ke'

#     def _get_access_token(self):
#         url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
#         response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
#         response.raise_for_status()
#         return response.json()['access_token']

#     def _generate_password(self):
#         timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#         data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
#         import base64
#         return base64.b64encode(data_to_encode.encode()).decode(), timestamp

#     def stk_push(self, phone_number, amount, order_number):
#         """Initiate Lipa Na M-Pesa Online (STK Push)"""
#         access_token = self._get_access_token()
#         password, timestamp = self._generate_password()

#         # Format phone: ensure it starts with 254
#         if phone_number.startswith('0'):
#             phone_number = '254' + phone_number[1:]
#         elif phone_number.startswith('+'):
#             phone_number = phone_number[1:]

#         url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
#         headers = {"Authorization": f"Bearer {access_token}"}
#         payload = {
#             "BusinessShortCode": self.shortcode,
#             "Password": password,
#             "Timestamp": timestamp,
#             "TransactionType": "CustomerPayBillOnline",
#             "Amount": int(amount),
#             "PartyA": phone_number,
#             "PartyB": self.shortcode,
#             "PhoneNumber": phone_number,
#             "CallBackURL": f"{self.callback_url}/api/orders/mpesa/callback",
#             "AccountReference": order_number,
#             "TransactionDesc": f"Payment for {order_number}",
#         }

#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         return response.json()
