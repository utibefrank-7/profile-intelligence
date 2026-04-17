from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer
from .services import intelligent_profile


class ProfileListCreateView(APIView):

    def post(self, request):
        name = request.data.get("name")

        if name is None:
            return Response(
                {"error": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        name = str(name).strip()

        if not name:
            return Response(
                {"error": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if name.isdigit():
            return Response(
                {"error": "Name must not be numeric"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        normalized_name = name.lower()

        existing = Profile.objects.filter(name=normalized_name).first()
        if existing:
            serializer = ProfileSerializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            enriched = intelligent_profile(normalized_name)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception:
            return Response(
                {"error": "Failed to reach external APIs"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        profile = Profile.objects.create(
            name=normalized_name,
            **enriched
        )

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        queryset = Profile.objects.all().order_by("id")

        gender = request.query_params.get("gender")
        country_id = request.query_params.get("country_id")
        age_group = request.query_params.get("age_group")

        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        if country_id:
            queryset = queryset.filter(country_id__iexact=country_id)
        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group)

        serializer = ProfileListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileDetailView(APIView):

    def get(self, request, id):
        profile = Profile.objects.filter(id=id).first()
        if not profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        profile = Profile.objects.filter(id=id).first()
        if not profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)