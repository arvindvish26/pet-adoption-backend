from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from .models import Cart, CartAccessory
from .serializers import (CartSerializer, CartListSerializer, AddToCartSerializer, 
                         UpdateCartItemSerializer, CartAccessorySerializer)
from petstore.permissions import IsOwnerOrAdmin

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CartListSerializer
        return CartSerializer
    
    def get_queryset(self):
        """
        Filter carts to only show user's own carts unless they're admin
        """
        if self.request.user.is_staff:
            return Cart.objects.all()
        return Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a cart"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Get current user's cart or create one if it doesn't exist"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to cart"""
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)
        
        if serializer.is_valid():
            accessory_id = serializer.validated_data['accessory_id']
            quantity = serializer.validated_data['quantity']
            
            # Check if item already exists in cart
            cart_accessory, created = CartAccessory.objects.get_or_create(
                cart=cart,
                accessory_id=accessory_id,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update quantity if item already exists
                cart_accessory.quantity += quantity
                cart_accessory.save()
            
            return Response({
                'message': 'Item added to cart successfully',
                'cart': CartSerializer(cart).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_item(self, request, pk=None):
        """Update cart item quantity"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        try:
            cart_item = CartAccessory.objects.get(id=item_id, cart=cart)
            serializer = UpdateCartItemSerializer(cart_item, data={'quantity': quantity})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Cart item updated successfully',
                    'cart': CartSerializer(cart).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except CartAccessory.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """Remove item from cart"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartAccessory.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response({
                'message': 'Item removed from cart successfully',
                'cart': CartSerializer(cart).data
            })
        except CartAccessory.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def clear_cart(self, request, pk=None):
        """Clear all items from cart"""
        cart = self.get_object()
        cart.cart_accessories.all().delete()
        return Response({
            'message': 'Cart cleared successfully',
            'cart': CartSerializer(cart).data
        })
    
    @action(detail=False, methods=['get'])
    def empty_carts(self, request):
        """Get all empty carts (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        empty_carts = Cart.objects.filter(cart_accessories__isnull=True)
        serializer = CartListSerializer(empty_carts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get cart statistics"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_carts = Cart.objects.count()
        empty_carts = Cart.objects.filter(cart_accessories__isnull=True).count()
        carts_with_items = total_carts - empty_carts
        
        return Response({
            'total_carts': total_carts,
            'empty_carts': empty_carts,
            'carts_with_items': carts_with_items,
            'active_cart_rate': round((carts_with_items / total_carts * 100), 2) if total_carts > 0 else 0
        })

class CartAccessoryViewSet(viewsets.ModelViewSet):
    queryset = CartAccessory.objects.all()
    serializer_class = CartAccessorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Filter cart accessories to only show user's own items unless they're admin
        """
        if self.request.user.is_staff:
            return CartAccessory.objects.all()
        return CartAccessory.objects.filter(cart__user=self.request.user)
