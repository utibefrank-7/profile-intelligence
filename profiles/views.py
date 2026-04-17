import requests
from uuid6 import uuid7
from django.db import IntegrityError, transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import (
    ProfileCreateSerializer,
    ProfileDetailSerializer,
    ProfileListSerializer,
)
from .utils import (
    normalize_name,
    classify_age_group,
    fetch_genderize,
    fetch_agify,
    fetch_nationalize,
    get_top_country,
    UpstreamValidationError,
)


@api_view(["GET", "POST"])
def profiles_collection(request):
    if request.method == "POST":
        return create_profile(request)
    return list_profiles(request)


@api_view(["GET", "DELETE"])
def profile_detail_view(request, id):
    if request.method == "GET":
        return get_profile(request, id)
    return delete_profile(request, id)


def create_profile(request):
    raw_name = request.data.get("name", None)

    if raw_name is None:
        return Response(
            {"status": "error", "message": "Missing or empty name"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(raw_name, str):
        return Response(
            {"status": "error", "message": "Invalid type"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if raw_name.strip() == "":
        return Response(
            {"status": "error", "message": "Missing or empty name"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    normalized_name = normalize_name(raw_name)

    existing = Profile.objects.filter(name=normalized_name).first()
    if existing:
        return Response(
            {
                "status": "success",
                "message": "Profile already exists",
                "data": ProfileDetailSerializer(existing).data,
            },
            status=status.HTTP_200_OK,
        )

    try:
        genderize_data = fetch_genderize(normalized_name)
        agify_data = fetch_agify(normalized_name)
        nationalize_data = fetch_nationalize(normalized_name)
    except UpstreamValidationError as exc:
        return Response(
            {"status": "502", "message": f"{exc.api_name} returned an invalid response"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except requests.RequestException:
        return Response(
            {"status": "error", "message": "Server failure"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    age = agify_data["age"]
    age_group = classify_age_group(age)
    country_id, country_probability = get_top_country(nationalize_data)

    try:
        with transaction.atomic():
            profile = Profile.objects.create(
                id=str(uuid7()),
                name=normalized_name,
                gender=genderize_data["gender"],
                gender_probability=genderize_data["probability"],
                sample_size=genderize_data["count"],
                age=age,
                age_group=age_group,
                country_id=country_id,
                country_probability=country_probability,
            )
    except IntegrityError:
        existing = Profile.objects.filter(name=normalized_name).first()
        if existing:
            return Response(
                {
                    "status": "success",
                    "message": "Profile already exists",
                    "data": ProfileDetailSerializer(existing).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": "error", "message": "Server failure"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "status": "success",
            "data": ProfileDetailSerializer(profile).data,
        },
        status=status.HTTP_201_CREATED,
    )


def get_profile(request, id):
    try:
        profile = Profile.objects.get(id=id)
    except Profile.DoesNotExist:
        return Response(
            {"status": "error", "message": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "status": "success",
            "data": ProfileDetailSerializer(profile).data,
        },
        status=status.HTTP_200_OK,
    )


def list_profiles(request):
    profiles = Profile.objects.all()

    gender = request.GET.get("gender")
    country_id = request.GET.get("country_id")
    age_group = request.GET.get("age_group")

    if gender:
        profiles = profiles.filter(gender__iexact=gender)
    if country_id:
        profiles = profiles.filter(country_id__iexact=country_id)
    if age_group:
        profiles = profiles.filter(age_group__iexact=age_group)

    data = ProfileListSerializer(profiles, many=True).data

    return Response(
        {
            "status": "success",
            "count": len(data),
            "data": data,
        },
        status=status.HTTP_200_OK,
    )


def delete_profile(request, id):
    try:
        profile = Profile.objects.get(id=id)
    except Profile.DoesNotExist:
        return Response(
            {"status": "error", "message": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    profile.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)