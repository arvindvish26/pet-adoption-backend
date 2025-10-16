from rest_framework import serializers
from .models import Pet
from accessories.serializers import CategorySerializer
from users.serializers import UserListSerializer

class PetSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    owner_detail = UserListSerializer(source='owner', read_only=True)
    formatted_adoption_fee = serializers.ReadOnlyField()
    
    class Meta:
        model = Pet
        fields = ['id', 'name', 'age', 'breed', 'category', 'category_detail', 
                 'vaccinated', 'city', 'status', 'image', 'owner', 'owner_detail',
                 'adoption_fee', 'currency', 'formatted_adoption_fee']
        read_only_fields = ['id', 'owner']
    
    def to_representation(self, instance):
        """Override to return clean image URL"""
        data = super().to_representation(instance)
        if instance.image and instance.image.name:
            # If it's a full URL (starts with http), return as is
            if instance.image.name.startswith('http'):
                data['image'] = instance.image.name
            # Otherwise, return the Django media URL
            else:
                data['image'] = instance.image.url
        return data
    
    def validate_age(self, value):
        if value <= 0:
            raise serializers.ValidationError("Age must be greater than 0")
        if value > 30:
            raise serializers.ValidationError("Age seems too high for a pet")
        return value
    
    def validate_status(self, value):
        if value not in ['Available', 'Adopted']:
            raise serializers.ValidationError("Status must be either 'Available' or 'Adopted'")
        return value

class PetListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing pets"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    formatted_adoption_fee = serializers.ReadOnlyField()
    
    class Meta:
        model = Pet
        fields = ['id', 'name', 'age', 'breed', 'category_name', 'vaccinated', 
                 'city', 'status', 'image', 'owner_name', 'adoption_fee', 'currency', 'formatted_adoption_fee']
    
    def to_representation(self, instance):
        """Override to return clean image URL"""
        data = super().to_representation(instance)
        if instance.image and instance.image.name:
            # If it's a full URL (starts with http), return as is
            if instance.image.name.startswith('http'):
                data['image'] = instance.image.name
            # Otherwise, return the Django media URL
            else:
                data['image'] = instance.image.url
        return data

class PetAdoptionSerializer(serializers.ModelSerializer):
    """Serializer for pet adoption"""
    class Meta:
        model = Pet
        fields = ['status']
    
    def validate_status(self, value):
        if value != 'Adopted':
            raise serializers.ValidationError("Status must be 'Adopted' for adoption")
        return value
