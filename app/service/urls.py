from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import GeoJsonViewSet

router = DefaultRouter()
router.register(r'layers', GeoJsonViewSet, basename='layer')

urlpatterns = [
    path('/', include(router.urls)),
]
