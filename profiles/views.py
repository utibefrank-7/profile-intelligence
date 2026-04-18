import requests
from django.db import IntegrityError, transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Profile


# ── Helpers ──────────────────────────────────────────────────────────────────

def error_response(message, http_status):
    return Response({"status": "error", "message": message}, status=http_status)


def get_age_group(age):
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    else:
        return "senior"


def format_profile(profile):
    return {
        "id": str(profile.id),
        "name": profile.name,
        "gender": profile.gender,
        "gender_probability": profile.gender_probability,
        "sample_size": profile.sample_size,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id,
        "country_probability": profile.country_probability,
        "created_at": profile.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def format_profile_list(profile):
    return {
        "id": str(profile.id),
        "name": profile.name,
        "gender": profile.gender,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id,
    }


# ── Views ─────────────────────────────────────────────────────────────────────

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


# ── Handlers ──────────────────────────────────────────────────────────────────

def create_profile(request):
    raw_name = request.data.get("name", None)

    if raw_name is None:
        return error_response("Missing or empty name", status.HTTP_400_BAD_REQUEST)

    if not isinstance(raw_name, str):
        return error_response("Invalid type", status.HTTP_422_UNPROCESSABLE_ENTITY)

    if raw_name.strip() == "":
        return error_response("Missing or empty name", status.HTTP_400_BAD_REQUEST)

    name = raw_name.strip().lower()

    existing = Profile.objects.filter(name=name).first()
    if existing:
        return Response(
            {"status": "success", "message": "Profile already exists", "data": format_profile(existing)},
            status=status.HTTP_200_OK,
        )

    try:
        gender_resp = requests.get("https://api.genderize.io", params={"name": name}, timeout=10)
        gender_data = gender_resp.json()
    except Exception:
        return error_response("Genderize returned an invalid response", status.HTTP_502_BAD_GATEWAY)

    try:
        age_resp = requests.get("https://api.agify.io", params={"name": name}, timeout=10)
        age_data = age_resp.json()
    except Exception:
        return error_response("Agify returned an invalid response", status.HTTP_502_BAD_GATEWAY)

    try:
        nation_resp = requests.get("https://api.nationalize.io", params={"name": name}, timeout=10)
        nation_data = nation_resp.json()
    except Exception:
        return error_response("Nationalize returned an invalid response", status.HTTP_502_BAD_GATEWAY)

    if not gender_data.get("gender") or gender_data.get("count", 0) == 0:
        return error_response("Genderize returned an invalid response", status.HTTP_502_BAD_GATEWAY)

    if not age_data.get("age"):
        return error_response("Agify returned an invalid response", status.HTTP_502_BAD_GATEWAY)

    countries = nation_data.get("country", [])
    if not countries:
        return error_response("Nationalize returned an invalid response", status.HTTP_502_BAD_GATEWAY)

    gender = gender_data["gender"]
    gender_probability = gender_data["probability"]
    sample_size = gender_data["count"]
    age = age_data["age"]
    age_group = get_age_group(age)
    top_country = max(countries, key=lambda x: x["probability"])
    country_id = top_country["country_id"]
    country_probability = top_country["probability"]

    try:
        with transaction.atomic():
            profile = Profile.objects.create(
                name=name,
                gender=gender,
                gender_probability=gender_probability,
                sample_size=sample_size,
                age=age,
                age_group=age_group,
                country_id=country_id,
                country_probability=country_probability,
            )
    except IntegrityError:
        existing = Profile.objects.filter(name=name).first()
        if existing:
            return Response(
                {"status": "success", "message": "Profile already exists", "data": format_profile(existing)},
                status=status.HTTP_200_OK,
            )
        return error_response("Server failure", status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(
        {"status": "success", "data": format_profile(profile)},
        status=status.HTTP_201_CREATED,
    )


def get_profile(request, id):
    try:
        profile = Profile.objects.get(id=id)
    except Profile.DoesNotExist:
        return error_response("Profile not found", status.HTTP_404_NOT_FOUND)

    return Response(
        {"status": "success", "data": format_profile(profile)},
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

    return Response(
        {
            "status": "success",
            "count": profiles.count(),
            "data": [format_profile_list(p) for p in profiles],
        },
        status=status.HTTP_200_OK,
    )


def delete_profile(request, id):
    try:
        profile = Profile.objects.get(id=id)
    except Profile.DoesNotExist:
        return error_response("Profile not found", status.HTTP_404_NOT_FOUND)

    profile.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)