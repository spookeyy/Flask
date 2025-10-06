
from flask import Flask, render_template, request, jsonify
import uuid
from datetime import datetime
from pesapal_client import PesapalClient
from config import config

app = Flask(__name__)

# initialize clients for both environments
sandbox_client = PesapalClient('sandbox')
production_client = PesapalClient('production')

# in-memory storage for demo
orders_store = {}

@app.route('/')
def index():
    return render_template('payment.html')


# only for testing, trying to register the ipn url
@app.route('/payment/register-ipn', methods=['POST'])
def register_ipn():
    """Manually register IPN URL"""
    try:
        environment = request.json.get('environment', 'sandbox')
        client = sandbox_client if environment == 'sandbox' else production_client
        
        response = client.register_ipn()
        
        return jsonify({
            'success': True,
            'message': 'IPN registered successfully',
            'ipn_id': client.ipn_id,
            'environment': environment
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to register IPN',
            'error': str(e)
        }), 400

# @app.route('/payment/initiate', methods=['POST'])
# def initiate_payment():
#     """Initiate payment process"""
#     try:
#         environment = request.form.get('environment', 'sandbox')
#         client = sandbox_client if environment == 'sandbox' else production_client

#         # generate unique order id
#         order_tracking_id = str(uuid.uuid4())

#         # prepare order data
#         order_data = {
#             "id": order_tracking_id,
#             "currency": request.form.get('currency', 'KES'),
#             "amount": float(request.form.get('amount')),
#             "description": request.form.get('description'),
#             "callback_url": client.config.CALLBACK_URL,
#             "notification_id": client.config.CONSUMER_KEY,
#             "billing_address": {
#                 "email_address": request.form.get('customer_email'),
#                 "phone_number": request.form.get('phone_number', ''),
#                 "first_name": "Customer",
#                 "last_name": "User"
#             },
#             # optional parameters
#             # "branch": client.config.BRANCH,
#             # "cancellation_url": client.config.CANCELLATION_URL,
#             # "redirect_mode": client.config.REDIRECT_MODE
#         }

#         # submit order to pesapal
#         response = client.submit_order(order_data)

#         # save order details in memory
#         orders_store[order_tracking_id] = {
#             'environment': environment,
#             'order_data': order_data,
#             'created_at': datetime.now().isoformat(),
#             'status': 'initiated'
#         }

#         # return payment redirect url
#         if response.get('redirect_url'):
#             return jsonify({
#                 'success': True,
#                 'message': 'Payment initiated successfully',
#                 'order_tracking_id': order_tracking_id,
#                 'redirect_url': response['redirect_url'],
#                 'environment': environment
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': 'Failed to get redirect url',
#                 'error': response
#             }), 400

#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': 'Failed to initiate payment',
#             'error': str(e)
#         }), 400


@app.route('/payment/initiate', methods=['POST'])
def initiate_payment():
    """Initiate payment process"""
    try:
        environment = request.form.get('environment', 'sandbox')
        client = sandbox_client if environment == 'sandbox' else production_client

        # Generate unique order id
        order_tracking_id = str(uuid.uuid4())

        # Prepare order data - FIXED: removed notification_id from here
        order_data = {
            "id": order_tracking_id,
            "currency": request.form.get('currency', 'KES'),
            "amount": float(request.form.get('amount')),
            "description": request.form.get('description'),
            "callback_url": client.config.CALLBACK_URL,
            "billing_address": {
                "email_address": request.form.get('customer_email'),
                "phone_number": request.form.get('phone_number', ''),
                "first_name": "Customer",
                "last_name": "User"
            },
            # Optional parameters
            # "branch": client.config.BRANCH,
            # "cancellation_url": client.config.CANCELLATION_URL,
            # "redirect_mode": client.config.REDIRECT_MODE
        }

        # Submit order to pesapal
        response = client.submit_order(order_data)

        # Save order details in memory
        orders_store[order_tracking_id] = {
            'environment': environment,
            'order_data': order_data,
            'created_at': datetime.now().isoformat(),
            'status': 'initiated'
        }

        # Return payment redirect url
        if response.get('redirect_url'):
            return jsonify({
                'success': True,
                'message': 'Payment initiated successfully',
                'order_tracking_id': order_tracking_id,
                'redirect_url': response['redirect_url'],
                'environment': environment
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to get redirect url',
                'error': response
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to initiate payment',
            'error': str(e)
        }), 400
    
# @app.route('/payment/callback', methods=['GET', 'POST'])
# def payment_callback():
#     """ Handle payment callback from pesapal"""
#     try:
#         # for get requests (user redirect)
#         if request.method == 'GET':
#             order_tracking_id = request.args.get('orderTrackingId')
#             order_merchant_reference =  request.args.get('orderMerchantReference')

#             return jsonify({
#                 'success': True,
#                 'message': 'Payment completed successfully',
#                 'order_tracking_id': order_tracking_id,
#                 'order_merchant_reference': order_merchant_reference
#             })

#         # for POST requests (IPN notification)
#         elif request.method == 'POST':
#             # notification_data  = request.get_json(force=True)
#             notification_data  = request.json
#             print("RAW IPN Payload:", notification_data)

#             if notification_data:
#                 order_tracking_id = notification_data.get('orderTrackingId')
#                 status = notification_data.get('status')

#                 # update order status in store
#                 if order_tracking_id in orders_store:
#                     orders_store[order_tracking_id]['status'] = status
#                     orders_store[order_tracking_id]['updated_at'] = datetime.now().isoformat()
#                     orders_store[order_tracking_id]['notification'] = notification_data

#                 return jsonify({
#                     'success': True,
#                     'message': 'IPN notification received successfully',
#                     'order_tracking_id': order_tracking_id,
#                     'status': status
#                 })
#             else:
#                 return jsonify({
#                     'success': False,
#                     'message': 'Failed to get IPN notification data',
#                 }), 400

#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': 'Failed to handle payment callback',
#             'error': str(e)
#         }), 400

@app.route('/payment/callback', methods=['GET', 'POST'])
def payment_callback():
    """ Handle payment callback from pesapal"""
    try:
        # for get requests (user redirect)
        if request.method == 'GET':
            order_tracking_id = request.args.get('OrderTrackingId')
            order_merchant_reference = request.args.get('OrderMerchantReference')

            # Update order status when user is redirected back
            if order_tracking_id in orders_store:
                orders_store[order_tracking_id]['status'] = 'completed'
                orders_store[order_tracking_id]['callback_received'] = datetime.now().isoformat()

            return jsonify({
                'success': True,
                'message': 'Payment completed successfully',
                'order_tracking_id': order_tracking_id,
                'order_merchant_reference': order_merchant_reference
            })

        # for POST requests (IPN notification)
        elif request.method == 'POST':
            notification_data = request.json
            print("RAW IPN Payload:", notification_data)

            if notification_data:
                order_tracking_id = notification_data.get('OrderTrackingId')
                status = notification_data.get('Status')
                payment_method = notification_data.get('PaymentMethod')

                # update order status in store
                if order_tracking_id in orders_store:
                    orders_store[order_tracking_id]['status'] = status
                    orders_store[order_tracking_id]['payment_method'] = payment_method
                    orders_store[order_tracking_id]['updated_at'] = datetime.now().isoformat()
                    orders_store[order_tracking_id]['notification'] = notification_data

                return jsonify({
                    'success': True,
                    'message': 'IPN notification received successfully',
                    'order_tracking_id': order_tracking_id,
                    'status': status
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to get IPN notification data',
                }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to handle payment callback',
            'error': str(e)
        }), 400
    
@app.route('/payment/status/<order_tracking_id>', methods=['GET'])
def payment_status(order_tracking_id):
    """ Check pament status """

    try:
        if order_tracking_id not in orders_store:
            return jsonify({'error': 'Order not found'}), 404
        
        order_info = orders_store[order_tracking_id]
        environment = order_info['environment']
        client = sandbox_client if environment == 'sandbox' else production_client
        
        # Get status from Pesapal
        status_response = client.get_transaction_status(order_tracking_id)
        
        # Update local store
        orders_store[order_tracking_id]['last_checked'] = datetime.now().isoformat()
        orders_store[order_tracking_id]['pesapal_status'] = status_response
        
        return jsonify({
            'order_tracking_id': order_tracking_id,
            'environment': environment,
            'local_status': order_info['status'],
            'pesapal_status': status_response
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/payment/methods', methods=['GET'])
def get_all_payment_methods():
    """Get available payment methods"""
    try:
        environment = request.args.get('environment', 'sandbox')
        client = sandbox_client if environment == 'sandbox' else production_client
        
        payment_methods_data = client.get_payment_methods()
        return jsonify({
            'environment': environment,
            'payment_methods': payment_methods_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/orders', methods=['GET'])
def list_orders():
    """List all orders (for testing purposes)"""
    return jsonify(orders_store)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    import os
    if os.getenv('FLASK_ENV') == 'development':
        import subprocess
        subprocess.run(["flask", "run"])
    else:
        app.run(host='0.0.0.0', port=5000, debug=False)