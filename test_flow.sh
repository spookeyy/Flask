#!/bin/bash

# Set variables
BASE_URL="http://localhost:5000"
ENVIRONMENT="sandbox"

echo "=== Pesapal Flask API Complete Test Flow ==="

# 1. Health Check
echo -e "\n1. Testing Health Check..."
curl -s -X GET "$BASE_URL/health" -H "Content-Type: application/json"

# 2. Get Payment Methods
echo -e "\n\n2. Getting Payment Methods..."
PAYMENT_METHODS_RESPONSE=$(curl -s -X GET "$BASE_URL/payment/methods?environment=$ENVIRONMENT" -H "Content-Type: application/json")
echo "$PAYMENT_METHODS_RESPONSE"

# 3. Initiate Payment
echo -e "\n3. Initiating Payment..."
PAYMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/payment/initiate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "environment=$ENVIRONMENT" \
  -d "amount=1500.00" \
  -d "currency=KES" \
  -d "description=Test Product Purchase" \
  -d "customer_email=customer@example.com" \
  -d "phone_number=254712345678")

echo "$PAYMENT_RESPONSE"

# Extract order_tracking_id from response
ORDER_TRACKING_ID=$(echo "$PAYMENT_RESPONSE" | grep -o '"order_tracking_id":"[^"]*' | cut -d'"' -f4)

if [ -n "$ORDER_TRACKING_ID" ]; then
    echo "Order Tracking ID: $ORDER_TRACKING_ID"
    
    # 4. Check Payment Status
    echo -e "\n4. Checking Payment Status..."
    curl -s -X GET "$BASE_URL/payment/status/$ORDER_TRACKING_ID" -H "Content-Type: application/json"
    
    # 5. Simulate IPN Notification
    echo -e "\n5. Simulating IPN Notification..."
    curl -s -X POST "$BASE_URL/payment/callback" \
      -H "Content-Type: application/json" \
      -d "{
        \"OrderTrackingId\": \"$ORDER_TRACKING_ID\",
        \"OrderMerchantReference\": \"TEST123\",
        \"Status\": \"COMPLETED\",
        \"PaymentMethod\": \"MPESA\",
        \"Description\": \"Payment completed successfully\"
      }"
    
    # 6. Check Status Again
    echo -e "\n6. Checking Updated Payment Status..."
    curl -s -X GET "$BASE_URL/payment/status/$ORDER_TRACKING_ID" -H "Content-Type: application/json"
    
    # 7. List All Orders
    echo -e "\n7. Listing All Orders..."
    curl -s -X GET "$BASE_URL/orders" -H "Content-Type: application/json"
    
else
    echo "Failed to extract Order Tracking ID"
fi

echo -e "\n=== Test Flow Complete ==="