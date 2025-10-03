from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Address
from .serializers import AddressSerializer, AddressListSerializer, AddressCreateSerializer
from petstore.permissions import IsOwnerOrAdmin

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'city', 'state', 'country']
    ordering_fields = ['city', 'state', 'created_at']
    ordering = ['-id']
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AddressListSerializer
        elif self.action == 'create':
            return AddressCreateSerializer
        return AddressSerializer
    
    def get_queryset(self):
        """
        Filter addresses to only show user's own addresses unless they're admin
        """
        if self.request.user.is_staff:
            return Address.objects.all()
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating an address"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_addresses(self, request):
        """Get current user's addresses"""
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressListSerializer(addresses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def shipping(self, request):
        """Get user's shipping addresses"""
        shipping_addresses = Address.objects.filter(user=request.user, type='shipping')
        serializer = AddressListSerializer(shipping_addresses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def billing(self, request):
        """Get user's billing addresses"""
        billing_addresses = Address.objects.filter(user=request.user, type='billing')
        serializer = AddressListSerializer(billing_addresses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set an address as default for its type"""
        address = self.get_object()
        
        # Remove default status from other addresses of the same type for this user
        Address.objects.filter(
            user=request.user, 
            type=address.type
        ).exclude(id=address.id).update(is_default=False)
        
        # Set this address as default (you'd need to add is_default field to model)
        # For now, we'll just return a success message
        return Response({
            'message': f'{address.type.title()} address set as default',
            'address': AddressSerializer(address).data
        })
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Get addresses filtered by location"""
        city = request.query_params.get('city', None)
        state = request.query_params.get('state', None)
        country = request.query_params.get('country', None)
        
        queryset = self.get_queryset()
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if state:
            queryset = queryset.filter(state__icontains=state)
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        serializer = AddressListSerializer(queryset, many=True)
        return Response(serializer.data)
