"""
Views for accounts app.

Demonstrates:
- ViewSets for RESTful API
- Custom actions
- Permission classes
- Filtering and pagination
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import get_user_model

from apps.accounts.serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, UserRoleSerializer, UserStatusSerializer
)
from apps.accounts.permissions import IsAdmin, CanManageUsers

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    
    Provides CRUD operations and custom actions for user management.
    """
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'email', 'username']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['create', 'destroy']:
            return [CanManageUsers()]
        elif self.action in ['update', 'partial_update']:
            # Users can update themselves, admins can update anyone
            if self.request.user.can_manage_users():
                return [IsAuthenticated()]
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        
        if user.can_manage_users():
            return User.objects.all()
        
        # Regular users can only see themselves
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def change_role(self, request, pk=None):
        """Change user role."""
        user = self.get_object()
        serializer = UserRoleSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user.change_role(serializer.validated_data['role'])
                return Response({
                    'message': 'User role updated successfully',
                    'role': user.role
                })
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def toggle_status(self, request, pk=None):
        """Toggle user active status."""
        user = self.get_object()
        
        if user.is_active:
            user.deactivate()
            message = 'User deactivated successfully'
        else:
            user.activate()
            message = 'User activated successfully'
        
        return Response({
            'message': message,
            'is_active': user.is_active
        })
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user's password."""
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Old password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[CanManageUsers])
    def statistics(self, request):
        """Get user statistics."""
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'admin_users': User.admins.count(),
            'power_users': User.power_users.count(),
            'regular_users': User.objects.filter(role='USER', is_active=True).count(),
        }
        return Response(stats)

