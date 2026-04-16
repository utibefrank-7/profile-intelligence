from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uuid6 import uuid7

from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer
from .services import intelligent_profile


class ProfileListCreateView(APIView):

    def post(self, request):
        name = request.data.get("name", "").strip()

        if not name:
            return Response(
                {"status": "error", "message": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(name, str):
            return Response(
                {"status": "error", "message": "Name must be a string"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        existing = Profile.objects.filter(name=name.lower()).first()
        if existing:
            serializer = ProfileSerializer(existing)
            return Response(
                {
                    "status": "success",
                    "message": "Profile already exists",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        try:
            enriched = intelligent_profile(name)
        except ValueError as e:
            return Response(
                {"status": "502", "message": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            print(f"ERROR: {e}")
            return Response(
                {"status": "error", "message": "Failed to reach external APIs"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        profile = Profile.objects.create(
            id=str(uuid7()),
            name=name.lower(),
            **enriched
        )

        serializer = ProfileSerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        queryset = Profile.objects.all()

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
        return Response(
            {"status": "success", "count": queryset.count(), "data": serializer.data},
            status=status.HTTP_200_OK
        )


class ProfileDetailView(APIView):

    def get(self, request, id):
        profile = Profile.objects.filter(id=id).first()
        if not profile:
            return Response(
                {"status": "error", "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProfileSerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request, id):
        profile = Profile.objects.filter(id=id).first()
        if not profile:
            return Response(
                {"status": "error", "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
