from django.contrib import admin
from django.urls import include, path

from .views import (DetachmentDetailView, DetachmentListCreateView,
                    ProfileDetailView, ProfileListCreateView, login_view,
                    register_view)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('api/v1/profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    path('api/v1/profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('api/v1/detachments/', DetachmentListCreateView.as_view(), name='detachment-list-create'),
    path('api/v1/detachments/<int:pk>/', DetachmentDetailView.as_view(), name='detachment-detail'),
]