from rest_framework import serializers


class TwoFAVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=6, max_length=6, trim_whitespace=True)
    temp_token = serializers.CharField(trim_whitespace=True)
