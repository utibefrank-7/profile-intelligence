from django.urls import path
from .views import profiles_collection, profile_detail_view

urlpatterns = [
    path("profiles/", profiles_collection, name="profiles-collection"),
    path("profiles/<str:id>/", profile_detail_view, name="profile-detail"),
]