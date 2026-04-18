from django.urls import path
from . import views

urlpatterns = [
    path('api/profiles', views.profiles_collection, name='profiles'),
    path('api/profiles/<str:id>', views.profile_detail_view, name='profile-detail'),
]