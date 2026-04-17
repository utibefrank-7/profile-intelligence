from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "name",
            "gender",
            "gender_probability",
            "sample_size",
            "age",
            "age_group",
            "country_id",
            "country_probability",
            "created_at",
        ]


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "name",
            "gender",
            "age",
            "age_group",
            "country_id",
        ]


class ProfileCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Name cannot be empty.")

        if value.isnumeric():
            raise serializers.ValidationError("Name cannot be numeric.")

        return value.lower()