from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'subject', 'subject_display', 
                 'message', 'status', 'status_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        return value.strip()
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()

class ContactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contact messages"""
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        return value.strip()
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()
    
    def validate_phone(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 characters long")
        return value.strip() if value else value

class ContactListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing contact messages"""
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'subject_display', 'status_display', 'created_at']

class ContactStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating contact status (admin only)"""
    
    class Meta:
        model = Contact
        fields = ['status']
    
    def validate_status(self, value):
        valid_statuses = ['new', 'in_progress', 'resolved', 'closed']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
