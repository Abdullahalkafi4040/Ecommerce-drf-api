from sslcommerz_lib import SSLCOMMERZ

def initiate_sslcommerz_payment(order, user, request):
    base_url = f"{request.scheme}://{request.get_host()}"

    ssl_settings = {
        'store_id': 'YOUR_STORE_ID',        # Sandbox Store ID
        'store_pass': 'YOUR_STORE_PASSWORD',# Sandbox Store Password
        'issandbox': True
    }
    sslcz = SSLCOMMERZ(ssl_settings)

    post_body = {
        'total_amount': float(order.total_price),
        'currency': "BDT",
        'tran_id': f"TXN-{order.id}",
        'success_url': f"{base_url}/api/v1/payments/success/",
        'fail_url': f"{base_url}/api/v1/payments/fail/",
        'cancel_url': f"{base_url}/api/v1/payments/cancel/",
        'cus_name': user.username,
        'cus_email': user.email if user.email else "user@example.com",
        'cus_add1': "Dhaka",
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'cus_phone': "01700000000",
        'shipping_method': "NO",
        'product_name': f"Order #{order.id}",
        'product_category': "Ecommerce",
        'product_profile': "general"
    }

    response = sslcz.createSession(post_body)
    return response.get('GatewayPageURL')