from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Contact
from .serializers import (ContactSerializer, ContactCreateSerializer, 
                         ContactListSerializer, ContactStatusUpdateSerializer)
from petstore.permissions import IsAdminUser

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'subject']
    search_fields = ['name', 'email', 'message']
    ordering_fields = ['created_at', 'name', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContactListSerializer
        elif self.action == 'create':
            return ContactCreateSerializer
        elif self.action == 'update_status':
            return ContactStatusUpdateSerializer
        return ContactSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]  # Allow anyone to submit contact forms
        elif self.action in ['list', 'retrieve', 'update_status']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]  # Only admins can view/manage contacts
        else:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better response"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                'message': 'Thank you for your message! We will get back to you within 24 hours.',
                'contact_id': contact.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get contact statistics"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_contacts = Contact.objects.count()
        new_contacts = Contact.objects.filter(status='new').count()
        in_progress_contacts = Contact.objects.filter(status='in_progress').count()
        resolved_contacts = Contact.objects.filter(status='resolved').count()
        closed_contacts = Contact.objects.filter(status='closed').count()
        
        # Subject breakdown
        subject_stats = Contact.objects.values('subject').annotate(count=Count('subject')).order_by('-count')
        
        # Recent contacts (last 7 days)
        from django.utils import timezone
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        recent_contacts = Contact.objects.filter(created_at__gte=week_ago).count()
        
        return Response({
            'total_contacts': total_contacts,
            'new_contacts': new_contacts,
            'in_progress_contacts': in_progress_contacts,
            'resolved_contacts': resolved_contacts,
            'closed_contacts': closed_contacts,
            'recent_contacts': recent_contacts,
            'subject_breakdown': list(subject_stats)
        })
    
    @action(detail=False, methods=['get'])
    def new(self, request):
        """Get all new contact messages"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_contacts = Contact.objects.filter(status='new')
        serializer = ContactListSerializer(new_contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update contact status (admin only)"""
        contact = self.get_object()
        serializer = ContactStatusUpdateSerializer(contact, data=request.data)
        
        if serializer.is_valid():
            old_status = contact.status
            serializer.save()
            return Response({
                'message': f'Contact status updated from {old_status} to {contact.status}',
                'contact': ContactSerializer(contact).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)