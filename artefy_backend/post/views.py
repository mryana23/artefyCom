import re
from rest_framework.decorators import api_view, permission_classes, APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import connection
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum

from communities.models import Community, CommunityMember
from .models import Hashtag, PostHashtag, Posts, PostMedia, Comments, PostInteractions
import os
import uuid
from .serializers import CommentSerializer, ContentReportSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import F
class HashtagSuggestionView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query or len(query) < 1:
            return Response([], status=status.HTTP_200_OK)
        
        # Get hashtags that match the query
        hashtags = Hashtag.objects.filter(
            Q(name__istartswith=query)
        ).order_by('-usage_count')[:10]  # Limit to 10 suggestions
        
        suggestions = [
            {
                'hashtag_id': hashtag.hashtag_id,
                'name': hashtag.name,
                'usage_count': hashtag.usage_count
            }
            for hashtag in hashtags
        ]
        
        return Response(suggestions, status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    try:
        # Create a new report with data from the request
        serializer = ContentReportSerializer(data=request.data)
        
        if serializer.is_valid():
            # Set the reporter_id to the current user's ID
            report = serializer.save(reporter_id=request.user.id)
            
            return Response({
                'message': 'Report submitted successfully',
                'report_id': report.report_id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    try:
        post = Posts.objects.get(pk=post_id)
        
        # Check if the current user owns the post
        # Since you're storing user_id as an integer, compare with request.user.id
        if post.user_id != request.user.id:
            return Response({'error': 'You do not have permission to delete this post'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response({'message': 'Post deleted successfully'})
    except Posts.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting post: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Fungsi untuk membuat postingan baru
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_post(request):
    try:
        user_id = request.user.id
        caption = request.data.get('caption', '')
        post_type = request.data.get('post_type', 'general')
        community_id = request.data.get('community_id', None)
        privacy = request.data.get('privacy', 'public')
        files = request.FILES.getlist('media')
        
        # If post_type is community, validate that the user is a member of the community
        if post_type == 'community' and community_id:
            try:
                member = CommunityMember.objects.get(
                    user_id=user_id,
                    community_id=community_id,
                    status='active'
                )
            except CommunityMember.DoesNotExist:
                return Response({
                    'error': 'You are not a member of this community'
                }, status=403)
        
        # Ensure media directories exist
        for folder in ['images', 'videos', 'documents']:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, folder), exist_ok=True)
        
        # Create post
        post = Posts.objects.create(
            user_id=user_id,
            caption=caption,
            post_type=post_type,
            community_id=community_id if post_type == 'community' else None,
            privacy=privacy
        )
        
        # Extract hashtags from caption
        hashtags = re.findall(r'#(\w+)', caption)
        
        # Save hashtags
        for tag_name in hashtags:
            # Check if hashtag exists
            tag = Hashtag.objects.filter(name=tag_name.lower()).first()
            
            if tag:
                # Update usage count
                Hashtag.objects.filter(hashtag_id=tag.hashtag_id).update(
                    usage_count=F('usage_count') + 1
                )
                hashtag_id = tag.hashtag_id
            else:
                # Create new hashtag
                new_tag = Hashtag.objects.create(name=tag_name.lower())
                hashtag_id = new_tag.hashtag_id
            
            # Create relationship between post and hashtag
            PostHashtag.objects.create(
                post_id=post.post_id,
                hashtag_id=hashtag_id
            )
        
        # Save uploaded media
        for file in files:
            file_ext = os.path.splitext(file.name)[1].lower()
            filename = f"{uuid.uuid4()}{file_ext}"
            
            # Validate file types
            allowed_image_types = ['.jpg', '.jpeg', '.png', '.gif']
            allowed_video_types = ['.mp4', '.mov', '.avi']
            allowed_document_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt']
            
            if file_ext not in allowed_image_types + allowed_video_types + allowed_document_types:
                raise ValueError(f'Unsupported file type: {file_ext}')
            
            # Determine media type
            if file_ext in allowed_video_types:
                media_type = 'video'
                folder = 'videos'
            elif file_ext in allowed_image_types:
                media_type = 'image'
                folder = 'images'
            else:
                media_type = 'document'
                folder = 'documents'
            
            # Determine file path
            filepath = os.path.join(settings.MEDIA_ROOT, folder, filename)
            
            # Save file
            with open(filepath, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # Save media information to database
            PostMedia.objects.create(
                post_id=post.post_id,
                media_type=media_type,
                media_url=f"{folder}/{filename}"
            )
            
        return Response({
            'message': 'Post successfully created',
            'post_id': post.post_id
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=400)
        
# New endpoint to get user communities
def get_user_communities_post(request, user_id):
    query = """
        SELECT c.id as community_id, c.name, c.category_id, c.photo_community, 
               CASE WHEN cm.role = 'admin' THEN TRUE ELSE FALSE END as is_admin
        FROM Communities c
        INNER JOIN Community_Members cm ON c.id = cm.community_id
        WHERE cm.user_id = %s AND cm.status = 'active'
        ORDER BY c.name
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [user_id])
        columns = [col[0] for col in cursor.description]
        communities = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse(communities, safe=False)
# Fungsi untuk mendapatkan daftar postingan
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.post_id,
                    p.caption,
                    p.created_at,
                    p.user_id,
                    users_user.username,
                    COUNT(DISTINCT c.comment_id) as comment_count,
                    (SELECT COUNT(*) FROM post_interactions WHERE post_id = p.post_id AND like_count > 0) as like_count,
                    (SELECT COUNT(*) FROM post_interactions WHERE post_id = p.post_id AND share_count > 0) as share_count,
                    GROUP_CONCAT(DISTINCT pm.media_url) as media_urls,
                    GROUP_CONCAT(DISTINCT pm.media_type) as media_types
                FROM posts p
                LEFT JOIN users_user ON p.user_id = users_user.id
                LEFT JOIN comments c ON p.post_id = c.post_id
                LEFT JOIN post_media pm ON p.post_id = pm.post_id
                GROUP BY p.post_id
                ORDER BY p.created_at DESC
            """)
            posts = cursor.fetchall()
            
            formatted_posts = []
            for post in posts:
                post_id = post[0]
                media_urls = post[8].split(',') if post[8] else []
                media_types = post[9].split(',') if post[9] else []
                
                media = []
                for url, type in zip(media_urls, media_types):
                    if url:
                        media.append({
                            'url': f'/media/{url}',
                            'type': type
                        })
                        
                # Check if the current user has liked this post
                try:
                    interaction = PostInteractions.objects.get(post_id=post_id, user_id=request.user.id)
                    is_liked = interaction.like_count > 0
                    is_shared = interaction.share_count > 0
                except PostInteractions.DoesNotExist:
                    is_liked = False
                    is_shared = False
                
                formatted_posts.append({
                    'post_id': post_id,
                    'caption': post[1],
                    'created_at': post[2],
                    'user_id': post[3],
                    'username': post[4],
                    'comment_count': post[5],
                    'like_count': post[6],
                    'share_count': post[7],
                    'media': media,
                    'is_liked': is_liked,
                    'is_shared': is_shared
                })
                
            return Response(formatted_posts)
            
    except Exception as e:
        import traceback
        print(f"Error fetching posts: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': 'Failed to fetch posts'}, status=500)
# Fungsi untuk membuat komentar pada postingan
@api_view(['POST'])
def create_comment(request, post_id):
    try:
        comment = Comments.objects.create(
            post_id=post_id,
            user_id=request.user.id,
            comment=request.data.get('comment')
        )
        return Response({'message': 'Komentar berhasil ditambahkan'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

# Fungsi untuk mendapatkan komentar dari sebuah postingan
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comments(request, post_id):
    try:
        comments = Comments.objects.filter(post_id=post_id).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Posts.DoesNotExist:
        return JsonResponse({'error': 'Post tidak ditemukan'}, status=404)

# Fungsi untuk melakukan interaksi dengan postingan (like/share)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def interact_with_post(request, post_id):
    try:
        # Enhanced debug logging
        print(f"==========================================")
        print(f"interact_with_post called with post_id: {post_id}")
        print(f"Request data: {request.data}")
        print(f"User: {request.user.id}")
        print(f"Request path: {request.path}")
        print(f"==========================================")
        
        interaction_type = request.data.get('type')
        print(f"Interaction type: {interaction_type}")
        
        try:
            interaction = PostInteractions.objects.get(
                post_id=post_id, 
                user_id=request.user.id
            )
            print(f"Existing interaction found for post_id {post_id}, user_id {request.user.id}")
        except PostInteractions.DoesNotExist:
            print(f"No existing interaction found for post_id {post_id}, user_id {request.user.id}, creating new")
            interaction = PostInteractions(
                post_id=post_id,
                user_id=request.user.id,
                like_count=0,
                share_count=0
            )
        
        if interaction_type == 'like':
            # Toggle like state
            was_liked = interaction.like_count > 0
            old_like_count = interaction.like_count
            interaction.like_count = 0 if was_liked else 1
            print(f"Changing like_count from {old_like_count} to {interaction.like_count} for post_id {post_id}")
            interaction.save()
            
            # Count total likes
            total_likes = PostInteractions.objects.filter(post_id=post_id, like_count__gt=0).count()
            print(f"Total likes for post_id {post_id}: {total_likes}")
            
            return Response({
                'status': 'success',
                'like_count': total_likes,
                'share_count': interaction.share_count,
                'is_liked': interaction.like_count > 0
            })
        
        elif interaction_type == 'share':
            # Increment share count
            old_share_count = interaction.share_count
            interaction.share_count += 1
            print(f"Incrementing share_count from {old_share_count} to {interaction.share_count} for post_id {post_id}")
            interaction.save()
            
            # Get total shares
            total_shares = PostInteractions.objects.filter(post_id=post_id).aggregate(
                total=Sum('share_count'))['total'] or 0
            print(f"Total shares for post_id {post_id}: {total_shares}")
            
            return Response({
                'status': 'success',
                'like_count': PostInteractions.objects.filter(post_id=post_id, like_count__gt=0).count(),
                'share_count': total_shares,
                'is_liked': interaction.like_count > 0
            })
        
        print(f"Unsupported action: {interaction_type}")
        return Response({'error': f'Unsupported action: {interaction_type}'}, status=400)
        
    except Exception as e:
        import traceback
        print(f"Error in interact_with_post: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': 'Terjadi kesalahan'}, status=500)