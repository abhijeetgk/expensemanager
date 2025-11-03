"""
Views for categories app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.categories.models import IncomeCategory, ExpenseCategory
from apps.categories.serializers import (
    IncomeCategorySerializer, ExpenseCategorySerializer,
    CategoryQuickCreateSerializer
)
from apps.accounts.permissions import (
    IsAdminOrReadOnly, CanManageCategories, CanCreateCategories
)


class IncomeCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing income categories."""
    
    queryset = IncomeCategory.objects.filter(is_active=True)
    serializer_class = IncomeCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_recurring', 'tax_applicable']
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name', 'created_at']
    
    def get_permissions(self):
        """Adjust permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanManageCategories()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def root_categories(self, request):
        """Get only root categories."""
        categories = self.queryset.filter(parent__isnull=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get subcategories of a category."""
        category = self.get_object()
        subcategories = category.subcategories.filter(is_active=True)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanCreateCategories])
    def quick_create(self, request):
        """Quick category creation for power users."""
        serializer = CategoryQuickCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            category = IncomeCategory.objects.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description', ''),
                color=serializer.validated_data.get('color', '#3B82F6'),
                icon=serializer.validated_data.get('icon', ''),
                created_by=request.user
            )
            
            response_serializer = self.get_serializer(category)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing expense categories."""
    
    queryset = ExpenseCategory.objects.filter(is_active=True)
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_essential', 'allows_split']
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name', 'created_at']
    
    def get_permissions(self):
        """Adjust permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanManageCategories()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def root_categories(self, request):
        """Get only root categories."""
        categories = self.queryset.filter(parent__isnull=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get subcategories of a category."""
        category = self.get_object()
        subcategories = category.subcategories.filter(is_active=True)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_budget(self, request):
        """Get categories with budget limits."""
        categories = self.queryset.filter(budget_limit__isnull=False)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanCreateCategories])
    def quick_create(self, request):
        """Quick category creation for power users."""
        serializer = CategoryQuickCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            category = ExpenseCategory.objects.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description', ''),
                color=serializer.validated_data.get('color', '#3B82F6'),
                icon=serializer.validated_data.get('icon', ''),
                created_by=request.user
            )
            
            response_serializer = self.get_serializer(category)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

