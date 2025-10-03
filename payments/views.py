from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Payment
from .serializers import (PaymentSerializer, PaymentListSerializer, PaymentCreateSerializer, 
                         PaymentStatusUpdateSerializer)
from petstore.permissions import IsAdminUser, IsOwnerOrAdmin

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    ordering_fields = ['paid_at', 'amount']
    ordering = ['-id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'update_status':
            return PaymentStatusUpdateSerializer
        return PaymentSerializer
    
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
        Filter payments to only show user's own payments unless they're admin
        """
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Get current user's payments"""
        payments = Payment.objects.filter(order__user=request.user)
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get payments filtered by status"""
        status_filter = request.query_params.get('status', None)
        if not status_filter:
            return Response(
                {'error': 'Status parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(status=status_filter)
        serializer = PaymentListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def update_status(self, request, pk=None):
        """Update payment status (admin only)"""
        payment = self.get_object()
        serializer = PaymentStatusUpdateSerializer(payment, data=request.data)
        
        if serializer.is_valid():
            old_status = payment.status
            serializer.save()
            
            # Update order status when payment is completed
            if payment.status == 'Completed' and old_status != 'Completed':
                payment.order.status = 'Processing'
                payment.order.save()
            
            return Response({
                'message': f'Payment status updated from {old_status} to {payment.status}',
                'payment': PaymentSerializer(payment).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def process_payment(self, request, pk=None):
        """Process a payment (simulate payment processing)"""
        payment = self.get_object()
        
        if payment.status != 'Pending':
            return Response(
                {'error': 'Payment can only be processed if status is Pending'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simulate payment processing
        payment.status = 'Completed'
        payment.paid_at = timezone.now()
        payment.save()
        
        # Update order status
        payment.order.status = 'Processing'
        payment.order.save()
        
        return Response({
            'message': 'Payment processed successfully',
            'payment': PaymentSerializer(payment).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def refund_payment(self, request, pk=None):
        """Refund a payment (admin only)"""
        payment = self.get_object()
        
        if payment.status != 'Completed':
            return Response(
                {'error': 'Only completed payments can be refunded'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'Refunded'
        payment.save()
        
        # Update order status to cancelled
        payment.order.status = 'Cancelled'
        payment.order.save()
        
        return Response({
            'message': 'Payment refunded successfully',
            'payment': PaymentSerializer(payment).data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def pending(self, request):
        """Get all pending payments (admin only)"""
        pending_payments = self.get_queryset().filter(status='Pending')
        serializer = PaymentListSerializer(pending_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def completed(self, request):
        """Get all completed payments (admin only)"""
        completed_payments = self.get_queryset().filter(status='Completed')
        serializer = PaymentListSerializer(completed_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def failed(self, request):
        """Get all failed payments (admin only)"""
        failed_payments = self.get_queryset().filter(status='Failed')
        serializer = PaymentListSerializer(failed_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payment statistics"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_payments = Payment.objects.count()
        pending_payments = Payment.objects.filter(status='Pending').count()
        completed_payments = Payment.objects.filter(status='Completed').count()
        failed_payments = Payment.objects.filter(status='Failed').count()
        refunded_payments = Payment.objects.filter(status='Refunded').count()
        
        total_revenue = Payment.objects.filter(status='Completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_refunds = Payment.objects.filter(status='Refunded').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'total_payments': total_payments,
            'pending_payments': pending_payments,
            'completed_payments': completed_payments,
            'failed_payments': failed_payments,
            'refunded_payments': refunded_payments,
            'total_revenue': float(total_revenue),
            'total_refunds': float(total_refunds),
            'net_revenue': float(total_revenue - total_refunds),
            'success_rate': round((completed_payments / total_payments * 100), 2) if total_payments > 0 else 0
        })
