from rest_framework import serializers
from .models import Category, Accessory

class CategorySerializer(serializers.ModelSerializer):
    accessories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'accessories_count']
        read_only_fields = ['id', 'accessories_count']
    
    def get_accessories_count(self, obj):
        return obj.accessories.count()

class CategoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing categories"""
    class Meta:
        model = Category
        fields = ['id', 'name']

class AccessorySerializer(serializers.ModelSerializer):
    category_detail = CategoryListSerializer(source='category', read_only=True)
    
    class Meta:
        model = Accessory
        fields = ['id', 'name', 'price', 'stock', 'description', 'category', 'category_detail', 'image']
        read_only_fields = ['id']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

class AccessoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing accessories"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Accessory
        fields = ['id', 'name', 'price', 'stock', 'category_name', 'image', 'is_in_stock']
    
    def get_is_in_stock(self, obj):
        return obj.stock > 0

class AccessoryStockUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating accessory stock"""
    class Meta:
        model = Accessory
        fields = ['stock']
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
