from .views import DefaultPermissionViewSet, AttributeMapper, ProductViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register(r'default_permission', DefaultPermissionViewSet)
router.register(r'product', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('attr', AttributeMapper.as_view())
]
