from django.urls import path
from . import views

urlpatterns = [
    # Create and list posts
    path('', views.get_posts, name='get-posts'),
    path('create/', views.create_post, name='create-post'),
    
    # Post interactions with proper post_id parameter
    path('<int:post_id>/comment/', views.create_comment, name='create-comment'),
    path('<int:post_id>/comments/', views.get_comments, name='get-comments'),  # Add this line
    path('<int:post_id>/interact/', views.interact_with_post, name='interact-with-post'),
    path('<int:post_id>/', views.delete_post, name='delete_post'),
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/create/', views.create_report, name='create_report'),
]