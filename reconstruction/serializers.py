from django.contrib.auth.models import User
from reconstruction.models import Work
from reconstruction.models import Reconstruction
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name"]
        extra_kwargs = {'password': {'write_only': True}}

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ["pk", "title", "description", "price", "imageUrl"]

class ReconstructionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')
    moderator_name = serializers.CharField(source='moderator.username', default='')
    class Meta:
        model = Reconstruction
        fields = ["pk", "status", "creation_date", "apply_date", "end_date", "user_name", "moderator_name", "place", "fundraising"]
        read_only_fields = ('fundraising',)
