from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Pet
from .serializers import PetSerializer, PetListSerializer, PetAdoptionSerializer
from petstore.permissions import IsAdminUser

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'vaccinated', 'city']
    search_fields = ['name', 'breed', 'city']
    ordering_fields = ['name', 'age', 'created_at']
    ordering = ['-id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PetListSerializer
        elif self.action == 'adopt':
            return PetAdoptionSerializer
        return PetSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Pet.objects.all()
        
        # Filter by status if requested
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category if requested
        category_filter = self.request.query_params.get('category', None)
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Filter by city if requested
        city_filter = self.request.query_params.get('city', None)
        if city_filter:
            queryset = queryset.filter(city__icontains=city_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def adopt(self, request, pk=None):
        """Adopt a pet"""
        pet = self.get_object()
        
        if pet.status == 'Adopted':
            return Response(
                {'error': 'This pet has already been adopted'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PetAdoptionSerializer(pet, data={'status': 'Adopted'})
        if serializer.is_valid():
            pet.owner = request.user
            pet.status = 'Adopted'
            pet.save()
            return Response({
                'message': f'Successfully adopted {pet.name}!',
                'pet': PetSerializer(pet).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available pets"""
        available_pets = self.get_queryset().filter(status='Available')
        serializer = PetListSerializer(available_pets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def adopted(self, request):
        """Get all adopted pets (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        adopted_pets = self.get_queryset().filter(status='Adopted')
        serializer = PetListSerializer(adopted_pets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_pets(self, request):
        """Get current user's adopted pets"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user_pets = self.get_queryset().filter(owner=request.user)
        serializer = PetListSerializer(user_pets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def make_available(self, request, pk=None):
        """Make an adopted pet available again (admin only)"""
        pet = self.get_object()
        pet.status = 'Available'
        pet.owner = None
        pet.save()
        return Response({
            'message': f'{pet.name} is now available for adoption',
            'pet': PetSerializer(pet).data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get pet statistics"""
        total_pets = Pet.objects.count()
        available_pets = Pet.objects.filter(status='Available').count()
        adopted_pets = Pet.objects.filter(status='Adopted').count()
        
        return Response({
            'total_pets': total_pets,
            'available_pets': available_pets,
            'adopted_pets': adopted_pets,
            'adoption_rate': round((adopted_pets / total_pets * 100), 2) if total_pets > 0 else 0
        })
