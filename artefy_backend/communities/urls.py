from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityViewSet
from . import views

router = DefaultRouter()
router.register(r'communities', CommunityViewSet, basename='community')

urlpatterns = [
    path('', include(router.urls)),
    path('communities/<int:community_id>/request-join/', views.request_join_community),
    path('community-join-requests/<int:request_id>/process/', views.process_join_request),
    path('communities/join-requests/pending/', views.get_pending_join_requests, name='get-pending-requests'),
    path('communities/join-requests/<int:request_id>/process/', views.process_join_request, name='process-join-request'),
]