from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Address
        fields = ['id', 'user', 'user_name', 'type', 'line1', 'line2', 'city', 'state', 'zip_code', 'country']
        read_only_fields = ['id', 'user']
    
    def validate_zip_code(self, value):
        if not value.strip():
            raise serializers.ValidationError("Zip code cannot be empty")
        return value.strip()
    
    def validate_city(self, value):
        if not value.strip():
            raise serializers.ValidationError("City cannot be empty")
        return value.strip().title()
    
    def validate_state(self, value):
        if not value.strip():
            raise serializers.ValidationError("State cannot be empty")
        return value.strip().title()
    
    def validate_country(self, value):
        if not value.strip():
            raise serializers.ValidationError("Country cannot be empty")
        return value.strip().title()

class AddressListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing addresses"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Address
        fields = ['id', 'user_name', 'type', 'line1', 'line2', 'city', 'state', 'zip_code', 'country']

class AddressCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating addresses"""
    class Meta:
        model = Address
        fields = ['type', 'line1', 'line2', 'city', 'state', 'zip_code', 'country']
    
    def validate(self, attrs):
        # Validate that the user doesn't have more than 2 addresses of the same type
        user = self.context['request'].user
        address_type = attrs['type']
        
        existing_count = Address.objects.filter(user=user, type=address_type).count()
        if existing_count >= 2:
            raise serializers.ValidationError(f"You can only have maximum 2 {address_type} addresses")
        
        return attrs
