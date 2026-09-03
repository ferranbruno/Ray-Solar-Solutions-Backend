from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.product import Product
from models.order import Order, OrderItem
from services.mpesa import MPesaService
from services.email import send_order_confirmation_email, send_order_status_email
import uuid

order_bp = Blueprint('orders', __name__)
mpesa = MPesaService()


def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


@order_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """Create order and initiate M-Pesa STK push"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, 404

    data = request.get_json()
    if not data or not data.get('items'):
        return {'error': 'Cart is empty'}, 400

    phone = data.get('phone', '').strip()
    if not phone:
        return {'error': 'Phone number is required for M-Pesa payment'}, 400

    cart_items = data['items']
    subtotal = 0
    order_items = []

    for item in cart_items:
        product = Product.query.get(item.get('id'))
        if not product or not product.is_active:
            return {'error': f'Product ID {item.get("id")} is no longer available'}, 400

        quantity = int(item.get('quantity', 1))
        if quantity < 1:
            return {'error': f'Invalid quantity for {product.name}'}, 400
        if quantity > product.stock:
            return {'error': f'Insufficient stock for {product.name}. Only {product.stock} available.'}, 400

        subtotal += product.price * quantity
        order_items.append({
            'product_id': product.id,
            'quantity': quantity,
            'unit_price': product.price,
        })

    delivery = 1500 if cart_items else 0
    total = subtotal + delivery

    try:
        order = Order(
            order_number=generate_order_number(),
            customer_id=user_id,
            total_amount=total,
            shipping_address=data.get('shipping_address', ''),
            notes=f"Phone: {phone} | M-PESA",
        )
        db.session.add(order)
        db.session.flush()

        for oi in order_items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=oi['product_id'],
                quantity=oi['quantity'],
                unit_price=oi['unit_price'],
            ))
            product = Product.query.get(oi['product_id'])
            product.stock -= oi['quantity']

        db.session.commit()

        # Initiate STK push
        try:
            stk_response = mpesa.stk_push(phone, total, order.order_number)
            print(f"STK Push response: {stk_response}")
            if stk_response.get('ResponseCode') == '0':
                order_data = order.to_dict()
                order_data['items'] = [
                    {
                        'name': Product.query.get(oi['product_id']).name if Product.query.get(oi['product_id']) else 'Product',
                        'quantity': oi['quantity'],
                        'total': int(oi['unit_price'] * oi['quantity']),
                    }
                    for oi in order_items
                ]
                order_data['total_amount'] = int(total)
                send_order_confirmation_email(user.email, order_data)
                return {
                    'message': 'Order placed. Check your phone for M-Pesa prompt.',
                    'order': order.to_dict(),
                    'checkout_request_id': stk_response.get('CheckoutRequestID'),
                }, 201
            else:
                order.status = 'cancelled'
                db.session.commit()
                return {'error': stk_response.get('CustomerMessage', 'M-Pesa request failed')}, 400
        except Exception as mpesa_error:
            print(f"STK Push error: {mpesa_error}")
            order.status = 'cancelled'
            db.session.commit()
            return {'error': f'M-Pesa error: {str(mpesa_error)}'}, 400

    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500


@order_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-Pesa payment callback"""
    data = request.get_json()

    stk_callback = data.get('Body', {}).get('stkCallback', {})
    result_code = stk_callback.get('ResultCode')
    result_desc = stk_callback.get('ResultDesc', '')
    order_number = stk_callback.get('CallbackMetadata', {}).get('Item', [{}])[0].get('Value', '') if stk_callback.get('CallbackMetadata') else ''

    # Extract order number from AccountReference in metadata
    metadata_items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
    account_ref = ''
    for item in metadata_items:
        if item.get('Name') == 'AccountReference':
            account_ref = item.get('Value', '')

    if result_code == 0:
        # Payment successful
        order = Order.query.filter_by(order_number=account_ref).first()
        if order:
            order.status = 'confirmed'
            order.notes = (order.notes or '') + f' | M-Pesa confirmed: {result_desc}'
            db.session.commit()
            customer = User.query.get(order.customer_id)
            if customer:
                send_order_status_email(customer.email, order.order_number, 'confirmed')
    else:
        # Payment failed — restore stock
        order = Order.query.filter_by(order_number=account_ref).first()
        if order and order.status != 'cancelled':
            for item in order.order_items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock += item.quantity
            order.status = 'cancelled'
            order.notes = (order.notes or '') + f' | M-Pesa failed: {result_desc}'
            db.session.commit()
            customer = User.query.get(order.customer_id)
            if customer:
                send_order_status_email(customer.email, order.order_number, 'cancelled')

    return {'ResultCode': 0, 'ResultDesc': 'OK'}


@order_bp.route('/mpesa/status/<order_number>', methods=['GET'])
@jwt_required()
def check_mpesa_status(order_number):
    """Check if an M-Pesa payment was confirmed"""
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(order_number=order_number, customer_id=user_id).first()

    if not order:
        return {'error': 'Order not found'}, 404

    return {
        'order_number': order.order_number,
        'status': order.status.value,
        'total_amount': order.total_amount,
    }, 200


@order_bp.route('', methods=['GET'])
@jwt_required()
def get_my_orders():
    """Get current user's orders"""
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).all()
    return {'orders': [o.to_dict() for o in orders]}, 200


@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a single order by ID"""
    user_id = int(get_jwt_identity())
    order = Order.query.get(order_id)

    if not order or order.customer_id != user_id:
        return {'error': 'Order not found'}, 404

    return {'order': order.to_dict()}, 200
