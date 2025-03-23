from rest_framework import serializers
from constructor import models


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['id', 'profile_img', 'first_name', 'last_name']


class BlogDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = models.Blog
        fields = ['id', 'author', 'logo', 'heading', 'short_description', 'content', 'updated_at']


class BlogListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = models.Blog
        fields = ['id', 'author', 'logo', 'heading', 'short_description', 'updated_at']
