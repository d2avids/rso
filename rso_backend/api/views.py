from rest_framework import viewsets
from users.models import (RSOUser, UserEducation, UserDocuments,
                          UserRegion, UserPrivacySettings, UserMedia, Region)
from .serializers import (RSOUserSerializer, UserEducationSerializer,
                          UserDocumentsSerializer,
                          UserRegionSerializer,
                          UserPrivacySettingsSerializer,
                          UserMediaSerializer,
                          RegionSerializer)


class RSOUserViewSet(viewsets.ModelViewSet):
    queryset = RSOUser.objects.all()
    serializer_class = RSOUserSerializer


class UserEducationViewSet(viewsets.ModelViewSet):
    queryset = UserEducation.objects.all()
    serializer_class = UserEducationSerializer

    def get_queryset(self):
        # Optionally, filter by user ID if required
        user_id = self.kwargs.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset


class UserDocumentsViewSet(viewsets.ModelViewSet):
    queryset = UserDocuments.objects.all()
    serializer_class = UserDocumentsSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset


class UserRegionViewSet(viewsets.ModelViewSet):
    queryset = UserRegion.objects.all()
    serializer_class = UserRegionSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset


class UserPrivacySettingsViewSet(viewsets.ModelViewSet):
    queryset = UserPrivacySettings.objects.all()
    serializer_class = UserPrivacySettingsSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset


class UserMediaViewSet(viewsets.ModelViewSet):
    queryset = UserMedia.objects.all()
    serializer_class = UserMediaSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


