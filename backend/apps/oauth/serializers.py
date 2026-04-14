from rest_framework import serializers

from .models import OAuthProvider


class OAuthLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=OAuthProvider.values)
    token = serializers.CharField(trim_whitespace=True)
