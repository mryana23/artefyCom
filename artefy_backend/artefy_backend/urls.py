"""
URL configuration for artefy_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# artefy_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from communities.views import get_user_communities, get_community_members
from post.views import get_user_communities_post, HashtagSuggestionView
from chat.views import get_group_messages, send_message
from django.urls import re_path
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('categories.urls')),
    path('api/', include('communities.urls')),
    path('api/posts/', include('post.urls')),
    path('api/user-communities/<int:user_id>/', get_user_communities, name='user_communities'),
    path('api/user-communities/post/<int:user_id>/', get_user_communities_post, name='user_communities_posts'),
    path('api/community-members/<int:community_id>/', get_community_members, name='community_members'),
    path('api/community/<int:community_id>/messages/', get_group_messages, name='group_messages'),
    path('api/community/<int:community_id>/send-message/', send_message, name='send_message'),
    path('api/hashtag-suggestions', HashtagSuggestionView.as_view(), name='hashtag-suggestions'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  

