from rest_framework import serializers
from .models import Community, CommunityMember
from django.db import connection 
from django.conf import settings

class CommunitySerializer(serializers.ModelSerializer):
    # Menambahkan field tambahan yang dihitung atau diambil dari database
    category_name = serializers.SerializerMethodField()  # Nama kategori komunitas
    member_count = serializers.SerializerMethodField()  # Jumlah anggota aktif dalam komunitas
    is_member = serializers.SerializerMethodField()  # Menentukan apakah user adalah anggota komunitas
    user_role = serializers.SerializerMethodField()  # Peran user dalam komunitas
    member_status = serializers.SerializerMethodField()  # Status keanggotaan user dalam komunitas
    photo_community = serializers.ImageField(required=False)
    class Meta:
        model = Community
        fields = '__all__'
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.communities_type = validated_data.get('communities_type', instance.communities_type)
        instance.status = validated_data.get('status', instance.status)
        instance.rules = validated_data.get('rules', instance.rules)
        
        # Only update subscription_price if communities_type is premium
        if validated_data.get('communities_type') == 'premium':
            instance.subscription_price = validated_data.get('subscription_price', instance.subscription_price)
        
        # Handle photo update if provided
        if 'photo_community' in validated_data:
            instance.photo_community = validated_data.get('photo_community')
            
        instance.save()
        return instance
    # Mengecek apakah user yang sedang login adalah anggota komunitas ini dengan status 'active'.
    def get_is_member(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
            
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 
                    FROM community_members 
                    WHERE community_id = %s 
                    AND user_id = %s 
                    AND status = 'active'
                ) as is_member
            """, [obj.id, request.user.id])
            return cursor.fetchone()[0]
    
    # Mengambil status keanggotaan user dalam komunitas ini.Jika user bukan anggota komunitas, akan mengembalikan None.
    def get_member_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
            
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT status FROM community_members 
                WHERE community_id = %s 
                AND user_id = %s
            """, [obj.id, request.user.id])
            result = cursor.fetchone()
            return result[0] if result else None
    
    # Mengambil nama kategori komunitas berdasarkan category_id yang tersimpan di tabel Community.
    def get_category_name(self, obj):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM categories_category 
                WHERE id = %s
            """, [obj.category_id])
            result = cursor.fetchone()
            return result[0] if result else None
        
    # Menghitung jumlah anggota komunitas yang memiliki status 'active'.
    def get_member_count(self, obj):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM community_members 
                WHERE community_id = %s AND status = 'active'
            """, [obj.id])
            return cursor.fetchone()[0]
        
    # Mengambil peran (role) user dalam komunitas jika statusnya 'active'. Jika user tidak memiliki peran atau bukan anggota, akan mengembalikan None.
    def get_user_role(self, obj):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT role FROM community_members 
                WHERE community_id = %s AND user_id = %s AND status = 'active'
            """, [obj.id, self.context['request'].user.id])
            result = cursor.fetchone()
            return result[0] if result else None
