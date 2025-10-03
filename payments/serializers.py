from rest_framework import serializers
from .models import Payment
from orders.serializers import OrderListSerializer

class PaymentSerializer(serializers.ModelSerializer):
    order_detail = OrderListSerializer(source='order', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'order_detail', 'payment_method', 'status', 'amount', 'paid_at']
        read_only_fields = ['id', 'paid_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def validate(self, attrs):
        order = attrs['order']
        amount = attrs['amount']
        
        # Ensure payment amount matches order total
        if amount != order.total_price:
            raise serializers.ValidationError(f"Payment amount must match order total: {order.total_price}")
        
        return attrs

class PaymentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing payments"""
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_total = serializers.DecimalField(source='order.total_price', max_digits=10, decimal_places=2, read_only=True)
    user_name = serializers.CharField(source='order.user.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'order_total', 'user_name', 'payment_method', 'status', 'amount', 'paid_at']

class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments"""
    class Meta:
        model = Payment
        fields = ['order', 'payment_method']
    
    def validate_order(self, value):
        # Ensure order exists and is not already paid
        if value.status == 'Delivered':
            raise serializers.ValidationError("Cannot create payment for delivered order")
        
        # Check if payment already exists for this order
        if Payment.objects.filter(order=value, status='Completed').exists():
            raise serializers.ValidationError("Payment already exists for this order")
        
        return value
    
    def create(self, validated_data):
        order = validated_data['order']
        
        # Create payment with order total as amount
        payment = Payment.objects.create(
            order=order,
            payment_method=validated_data['payment_method'],
            amount=order.total_price,
            status='Pending'
        )
        
        return payment

class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment status"""
    class Meta:
        model = Payment
        fields = ['status']
    
    def validate_status(self, value):
        valid_statuses = ['Pending', 'Completed', 'Refunded', 'Failed']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        new_status = validated_data['status']
        
        # Set paid_at when payment is completed
        if new_status == 'Completed' and instance.status != 'Completed':
            validated_data['paid_at'] = timezone.now()
        
        return super().update(instance, validated_data)
