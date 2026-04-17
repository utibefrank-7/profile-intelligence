from rest_framework import serializers
from .models import Profile


class ProfileCreateSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Invalid type")
        if value.strip() == "":
            raise serializers.ValidationError("Missing or empty name")
        return value


class ProfileDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

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

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")


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