from rest_framework import serializers
from .models import Cart, CartAccessory
from accessories.serializers import AccessoryListSerializer

class CartAccessorySerializer(serializers.ModelSerializer):
    accessory_detail = AccessoryListSerializer(source='accessory', read_only=True)
    
    class Meta:
        model = CartAccessory
        fields = ['id', 'accessory', 'accessory_detail', 'quantity']
        read_only_fields = ['id']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

class CartSerializer(serializers.ModelSerializer):
    cart_accessories = CartAccessorySerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_name', 'cart_accessories', 'total_items', 'total_price', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_total_items(self, obj):
        return sum(cart_accessory.quantity for cart_accessory in obj.cart_accessories.all())
    
    def get_total_price(self, obj):
        total = 0
        for cart_accessory in obj.cart_accessories.all():
            total += cart_accessory.accessory.price * cart_accessory.quantity
        return total

class CartListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing carts"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user_name', 'total_items', 'total_price', 'created_at']
    
    def get_total_items(self, obj):
        return sum(cart_accessory.quantity for cart_accessory in obj.cart_accessories.all())
    
    def get_total_price(self, obj):
        total = 0
        for cart_accessory in obj.cart_accessories.all():
            total += cart_accessory.accessory.price * cart_accessory.quantity
        return total

class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    accessory_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_accessory_id(self, value):
        from accessories.models import Accessory
        try:
            accessory = Accessory.objects.get(id=value)
            if accessory.stock <= 0:
                raise serializers.ValidationError("This accessory is out of stock")
        except Accessory.DoesNotExist:
            raise serializers.ValidationError("Accessory does not exist")
        return value
    
    def validate(self, attrs):
        from accessories.models import Accessory
        accessory = Accessory.objects.get(id=attrs['accessory_id'])
        if attrs['quantity'] > accessory.stock:
            raise serializers.ValidationError(f"Only {accessory.stock} items available in stock")
        return attrs

class UpdateCartItemSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity"""
    class Meta:
        model = CartAccessory
        fields = ['quantity']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        
        # Check stock availability
        if hasattr(self, 'instance') and self.instance:
            if value > self.instance.accessory.stock:
                raise serializers.ValidationError(f"Only {self.instance.accessory.stock} items available in stock")
        
        return value
