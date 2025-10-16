from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Accessory
from .serializers import (CategorySerializer, CategoryListSerializer, 
                         AccessorySerializer, AccessoryListSerializer, 
                         AccessoryStockUpdateSerializer)
from petstore.permissions import IsAdminUser

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def accessories(self, request, pk=None):
        """Get all accessories in a category"""
        category = self.get_object()
        accessories = category.accessories.all()
        serializer = AccessoryListSerializer(accessories, many=True)
        return Response(serializer.data)

class AccessoryViewSet(viewsets.ModelViewSet):
    queryset = Accessory.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'stock', 'currency']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    ordering = ['-id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AccessoryListSerializer
        elif self.action == 'update_stock':
            return AccessoryStockUpdateSerializer
        return AccessorySerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Accessory.objects.all()
        
        # Filter by category if requested
        category_filter = self.request.query_params.get('category', None)
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Filter by price range if requested
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        return queryset
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def update_stock(self, request, pk=None):
        """Update accessory stock"""
        accessory = self.get_object()
        serializer = AccessoryStockUpdateSerializer(accessory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': f'Stock updated for {accessory.name}',
                'accessory': AccessorySerializer(accessory).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """Get all accessories that are in stock"""
        in_stock_accessories = self.get_queryset().filter(stock__gt=0)
        serializer = AccessoryListSerializer(in_stock_accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get all accessories that are out of stock (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        out_of_stock_accessories = self.get_queryset().filter(stock=0)
        serializer = AccessoryListSerializer(out_of_stock_accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get accessories with low stock (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        low_stock_threshold = int(request.query_params.get('threshold', 10))
        low_stock_accessories = self.get_queryset().filter(
            stock__gt=0, 
            stock__lte=low_stock_threshold
        )
        serializer = AccessoryListSerializer(low_stock_accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get accessory statistics"""
        total_accessories = Accessory.objects.count()
        in_stock_count = Accessory.objects.filter(stock__gt=0).count()
        out_of_stock_count = Accessory.objects.filter(stock=0).count()
        
        return Response({
            'total_accessories': total_accessories,
            'in_stock': in_stock_count,
            'out_of_stock': out_of_stock_count,
            'availability_rate': round((in_stock_count / total_accessories * 100), 2) if total_accessories > 0 else 0
        })
