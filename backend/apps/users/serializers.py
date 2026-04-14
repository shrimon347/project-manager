from rest_framework import serializers


class ProfileUpdateSerializer(serializers.Serializer):
    """Validate profile update payload.

    Inputs:
    - name: optional display name
    - profilePicture: optional avatar image

    Outputs:
    - validated_data with profile fields to update
    """

    name = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    profilePicture = serializers.ImageField(required=False, allow_null=True)
