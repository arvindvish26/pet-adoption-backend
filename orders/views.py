from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from .models import Order
from .serializers import (OrderSerializer, OrderListSerializer, OrderCreateSerializer, 
                         OrderStatusUpdateSerializer)
from petstore.permissions import IsAdminUser, IsOwnerOrAdmin

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'user']
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        elif self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter orders to only show user's own orders unless they're admin
        """
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get current user's orders"""
        orders = Order.objects.filter(user=request.user)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get orders filtered by status"""
        status_filter = request.query_params.get('status', None)
        if not status_filter:
            return Response(
                {'error': 'Status parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(status=status_filter)
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data)
        
        if serializer.is_valid():
            old_status = order.status
            serializer.save()
            
            return Response({
                'message': f'Order status updated from {old_status} to {order.status}',
                'order': OrderSerializer(order).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel_order(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        # Only allow cancellation if order is still processing
        if order.status != 'Processing':
            return Response(
                {'error': 'Only processing orders can be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'Cancelled'
        order.save()
        
        return Response({
            'message': 'Order cancelled successfully',
            'order': OrderSerializer(order).data
        })
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Get order tracking information"""
        order = self.get_object()
        
        tracking_info = {
            'order_id': order.id,
            'status': order.status,
            'created_at': order.created_at,
            'user': order.user.username,
            'total_price': order.total_price,
            'shipping_address': {
                'line1': order.shipping_address.line1,
                'city': order.shipping_address.city,
                'state': order.shipping_address.state,
                'zip_code': order.shipping_address.zip_code
            }
        }
        
        return Response(tracking_info)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def processing(self, request):
        """Get all processing orders (admin only)"""
        processing_orders = self.get_queryset().filter(status='Processing')
        serializer = OrderListSerializer(processing_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def shipped(self, request):
        """Get all shipped orders (admin only)"""
        shipped_orders = self.get_queryset().filter(status='Shipped')
        serializer = OrderListSerializer(shipped_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def delivered(self, request):
        """Get all delivered orders (admin only)"""
        delivered_orders = self.get_queryset().filter(status='Delivered')
        serializer = OrderListSerializer(delivered_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_orders = Order.objects.count()
        processing_orders = Order.objects.filter(status='Processing').count()
        shipped_orders = Order.objects.filter(status='Shipped').count()
        delivered_orders = Order.objects.filter(status='Delivered').count()
        cancelled_orders = Order.objects.filter(status='Cancelled').count()
        
        total_revenue = Order.objects.filter(status='Delivered').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        return Response({
            'total_orders': total_orders,
            'processing_orders': processing_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': float(total_revenue),
            'delivery_rate': round((delivered_orders / total_orders * 100), 2) if total_orders > 0 else 0
        })
