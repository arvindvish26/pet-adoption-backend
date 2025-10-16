from rest_framework import serializers
from .models import Order
from carts.serializers import CartSerializer
from addresses.serializers import AddressSerializer
from users.serializers import UserListSerializer

class OrderSerializer(serializers.ModelSerializer):
    user_detail = UserListSerializer(source='user', read_only=True)
    cart_detail = CartSerializer(source='cart', read_only=True)
    shipping_address_detail = AddressSerializer(source='shipping_address', read_only=True)
    billing_address_detail = AddressSerializer(source='billing_address', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_detail', 'cart', 'cart_detail', 'total_price', 
                 'shipping_address', 'shipping_address_detail', 'billing_address', 
                 'billing_address_detail', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_total_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total price must be greater than 0")
        return value
    
    def validate(self, attrs):
        # Ensure cart has items
        cart = attrs['cart']
        if not cart.cart_accessories.exists():
            raise serializers.ValidationError("Cannot create order with empty cart")
        
        # Ensure addresses belong to the user
        user = attrs['user']
        shipping_address = attrs['shipping_address']
        billing_address = attrs['billing_address']
        
        if shipping_address.user != user:
            raise serializers.ValidationError("Shipping address must belong to the user")
        if billing_address.user != user:
            raise serializers.ValidationError("Billing address must belong to the user")
        
        return attrs

class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing orders"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    cart_total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user_name', 'total_price', 'status', 'created_at', 'cart_total_items']
    
    def get_cart_total_items(self, obj):
        return sum(cart_accessory.quantity for cart_accessory in obj.cart.cart_accessories.all())

class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    class Meta:
        model = Order
        fields = ['id', 'cart', 'shipping_address', 'billing_address', 'total_price', 'status', 'created_at']
        read_only_fields = ['id', 'total_price', 'status', 'created_at']
    
    def validate_cart(self, value):
        # Ensure cart has items
        if not value.cart_accessories.exists():
            raise serializers.ValidationError("Cannot create order with empty cart")
        
        # Ensure cart belongs to the user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Cart must belong to the user")
        
        return value
    
    def validate_shipping_address(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Shipping address must belong to the user")
        return value
    
    def validate_billing_address(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Billing address must belong to the user")
        return value
    
    def create(self, validated_data):
        cart = validated_data['cart']
        
        # Calculate total price
        total_price = sum(
            cart_accessory.accessory.price * cart_accessory.quantity 
            for cart_accessory in cart.cart_accessories.all()
        )
        
        # Create order
        order = Order.objects.create(
            user=self.context['request'].user,
            cart=cart,
            total_price=total_price,
            shipping_address=validated_data['shipping_address'],
            billing_address=validated_data['billing_address'],
            status='Processing'
        )
        
        return order

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status"""
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        valid_statuses = ['Processing', 'Shipped', 'Delivered', 'Cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
