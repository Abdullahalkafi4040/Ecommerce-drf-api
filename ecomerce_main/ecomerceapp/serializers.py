from django.db import transaction
from rest_framework import serializers
from .models import Cart, CartItem, Category, Order, OrderItem, Product


class CategorySerializer(serializers.ModelSerializer):

  class Meta:
    model = Category
    fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
  
  category_details = CategorySerializer(source='category', read_only=True)

  class Meta:
    model = Product
    fields = [
        'id',
        'category',
        'category_details',
        'name',
        'description',
        'price',
        'stock',
        'image',
        'created_at',
    ]


class CartItemSerializer(serializers.ModelSerializer):
  
  product_name = serializers.ReadOnlyField(source='product.name')
  product_price = serializers.ReadOnlyField(source='product.price')

  class Meta:
    model = CartItem
    fields = ['id', 'product', 'product_name', 'product_price', 'quantity']

  def validate_quantity(self, value):
    if value <= 0:
      raise serializers.ValidationError('পরিমাণ অবশ্যই ১ বা তার বেশি হতে হবে।')
    return value

  def validate(self, attrs):
    product = attrs.get('product')
    quantity = attrs.get('quantity', 1)

    
    if product.stock < quantity:
      raise serializers.ValidationError(
          {'quantity': f'স্টক খালি! সর্বোচ্চ {product.stock} টি কিনতে পারবেন।'}
      )

    return attrs

  def create(self, validated_data):
    user = self.context['request'].user
    
    cart, _ = Cart.objects.get_or_create(user=user)
    product = validated_data['product']
    quantity = validated_data['quantity']

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': quantity}
    )

    if not created:
      cart_item.quantity += quantity
      cart_item.save()

    return cart_item


class OrderItemSerializer(serializers.ModelSerializer):
  
  product_name = serializers.ReadOnlyField(source='product.name')

  class Meta:
    model = OrderItem
    fields = ['id', 'product', 'product_name', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
  
  items = OrderItemSerializer(many=True, read_only=True)
  user = serializers.ReadOnlyField(source='user.username')

  class Meta:
    model = Order
    fields = [
        'id',
        'user',
        'total_price',
        'status',
        'payment_status',
        'transaction_id',
        'created_at',
        'items',
    ]
    read_only_fields = [
        'total_price',
        'status',
        'payment_status',
        'transaction_id',
    ]

  @transaction.atomic
  def create(self, validated_data):
    user = self.context['request'].user
    cart = getattr(user, 'cart', None)

    if not cart or not cart.items.exists():
      raise serializers.ValidationError({'detail': 'আপনার কার্ট খালি!'})

    cart_items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    for item in cart_items:
      if item.product.stock < item.quantity:
        raise serializers.ValidationError(
            {'detail': f'{item.product.name} স্টকে পর্যাপ্ত নেই!'}
        )

    
    order = Order.objects.create(user=user, total_price=total_price)

    order_items = [
        OrderItem(
            order=order,
            product=item.product,
            price=item.product.price,  
            quantity=item.quantity,
        )
        for item in cart_items
    ]
    OrderItem.objects.bulk_create(order_items)

    for item in cart_items:
      item.product.stock -= item.quantity
      item.product.save()

    
    cart.items.all().delete()

    return order