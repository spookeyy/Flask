from datetime import datetime, timedelta
import requests
import json
import base64
import hashlib
import hmac # hmac is for hashing
import uuid
from config import config


class PesapalClient:
    def __init__(self, environment='sandbox'):
        self.config = config[environment]()
        self.base_url = self.config.PESAPAL_BASE_URL
        self.consumer_key = self.config.CONSUMER_KEY
        self.consumer_secret = self.config.CONSUMER_SECRET
        # self.branch = self.config.BRANCH
        # self.cancellation_url = self.config.CANCELLATION_URL
        # self.redirect_mode = self.config.REDIRECT_MODE
        self.access_token = None
        self.token_expiry = None
        self.ipn_id = None

        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("Consumer key and secre must be provided")
        
    def _get_auth_token(self):
        """Get authentication token from pesapal"""
        # return cached token it it is still valid
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        # get new token
        url = f"{self.base_url}/api/Auth/RequestToken"
        payload = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.access_token = data["token"]

            # set token expiry(typical 1hr, refresh after 55 minutes)
            self.token_expiry = datetime.now() + timedelta(seconds=3300)   # 55 minutes in seconds

            return self.access_token
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get authentication token: {e}")
        
    def _get_headers(self):
        """Get headers with authentication token"""
        token = self._get_auth_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    


    def register_ipn(self):
        """
        Register IPN notification URL with Pesapal
        Returns the IPN ID that should be used in order submissions
        """
        url = f"{self.base_url}/api/URLSetup/RegisterIPN"
        
        payload = {
            "url": f"{self.config.CALLBACK_URL}",
            "ipn_notification_type": "POST"
        }

        try:
            headers = self._get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.ipn_id = data.get('ipn_id')
            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"IPN registration failed: {e}")
    
    def submit_order(self, order_data):
        """
        Submit order to pesapal

        Args:
            order_data (dict): Order data
        """
        url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"

        # Generate unique order tracking id if not provided
        if 'order_tracking_id' not in order_data:
            order_data['order_tracking_id'] = str(uuid.uuid4())

        # Validate required fields
        required_fields = ['amount', 'currency', 'description', 'callback_url', 'billing_address']
        
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")

        # Register IPN if not already registered
        if not self.ipn_id:
            self.register_ipn()
        
        if not self.ipn_id:
            raise Exception("Failed to get IPN ID from registration")

        # Use the IPN ID instead of consumer key
        order_data['notification_id'] = self.ipn_id

        try:
            headers = self._get_headers()
            response = requests.post(url, json=order_data, headers=headers, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Order submission failed: {e}")
    
    # def submit_order(self, order_data):
    #     """
    #     Submit order to pesapal

    #     Args:
    #         order_data (dict): Order data
    #     """
    #     url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"

    #     # Generate unique order tracking id if not provided
    #     if 'order_tracking_id' not in order_data:
    #         order_data['order_tracking_id'] = str(uuid.uuid4())

    #     # Validate required fields
    #     required_fields = ['amount', 'currency', 'description', 'callback_url', 'notification_id', 'billing_address']
        
    #     for field in required_fields:
    #         if field not in order_data:
    #             raise ValueError(f"Missing required field: {field}")

    #     # FIX: Register IPN and get ipn_id first
    #     try:
    #         # Register IPN URL
    #         ipn_response = self.register_ipn()
    #         ipn_id = ipn_response.get('ipn_id')
            
    #         if not ipn_id:
    #             raise Exception("Failed to get IPN ID from registration")

    #         # Add ipn_id to order data
    #         order_data['ipn_notification_id'] = ipn_id

    #         headers = self._get_headers()
    #         response = requests.post(url, json=order_data, headers=headers, timeout=30)
    #         response.raise_for_status()

    #         return response.json()

    #     except requests.exceptions.RequestException as e:
    #         raise Exception(f"Order submission failed: {e}")
            
    def get_transaction_status(self, order_tracking_id):
        """
            Get transaction status

            Args:
                order_tracking_id (str): Order tracking id
        """

        url = f"{self.base_url}/api/Transactions/GetTransactionStatus"
        params = {
            "orderTrackingId": order_tracking_id
        }

        try:
            headers = self._get_headers()
            response = requests.get(url, params=params, headers=headers, timeout=30)

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Transaction status check failed: {e}")
        
    # def get_payment_methods(self):
    #     """Get available payment methods"""
    #     url = f"{self.base_url}/api/PaymentDetails/GetPaymentMethods"
        
    #     try:
    #         headers = self._get_headers()
    #         response = requests.get(url, headers=headers, timeout=30)
    #         response.raise_for_status()
            
    #         return response.json()
            
    #     except requests.exceptions.RequestException as e:
    #         raise Exception(f"Failed to get payment methods: {str(e)}")

    def get_payment_methods(self):
        """Get available payment methods"""
        url = f"{self.base_url}/api/Transactions/GetPaymentMethods"
        
        try:
            headers = self._get_headers()
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get payment methods: {str(e)}")
        
        
    def register_ipn(self):
        """
        Register IPN notification URL with Pesapal
        Returns the IPN ID that should be used in order submissions
        """
        url = f"{self.base_url}/api/URLSetup/RegisterIPN"
        
        payload = {
            "url": f"{self.config.CALLBACK_URL}",
            "ipn_notification_type": "POST"
        }

        try:
            headers = self._get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.ipn_id = data.get('ipn_id')
            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"IPN registration failed: {e}")

