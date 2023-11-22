from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import (Region, RSOUser, UserDocuments, UserEducation,
                          UserMedia, UserPrivacySettings, UserRegion,
                          UserStatementDocuments)

from .mixins import ListRetrieveViewSet, ListRetrieveUpdateViewSet
from .serializers import (RegionSerializer, RSOUserSerializer,
                          UserDocumentsSerializer, UserEducationSerializer,
                          UserMediaSerializer, UserPrivacySettingsSerializer,
                          UserRegionSerializer,
                          UserStatementDocumentsSerializer)


class RSOUserViewSet(ListRetrieveUpdateViewSet):
    queryset = RSOUser.objects.all()
    serializer_class = RSOUserSerializer

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=RSOUserSerializer,
    )
    def me(self, request, pk=None):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(self.get_serializer(request.user).data)


class RegionViewSet(ListRetrieveViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class BaseUserViewSet(viewsets.ModelViewSet):
    """
    Базовый вьюсет для расширения дочерними вьюсетами для моделей
    связанными с User.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_pk', None)
        user = get_object_or_404(
            RSOUser, id=user_id
        ) if user_id else self.request.user
        serializer.save(user=user)


class UserEducationViewSet(BaseUserViewSet):
    queryset = UserEducation.objects.all()
    serializer_class = UserEducationSerializer

    def get_object(self):
        return get_object_or_404(UserEducation, user=self.request.user)


class UserDocumentsViewSet(BaseUserViewSet):
    queryset = UserDocuments.objects.all()
    serializer_class = UserDocumentsSerializer

    def get_object(self):
        return get_object_or_404(UserDocuments, user=self.request.user)


class UserRegionViewSet(BaseUserViewSet):
    queryset = UserRegion.objects.all()
    serializer_class = UserRegionSerializer

    def get_object(self):
        return get_object_or_404(UserRegion, user=self.request.user)


class UserPrivacySettingsViewSet(BaseUserViewSet):
    queryset = UserPrivacySettings.objects.all()
    serializer_class = UserPrivacySettingsSerializer

    def get_object(self):
        return get_object_or_404(UserPrivacySettings, user=self.request.user)


class UserMediaViewSet(BaseUserViewSet):
    queryset = UserMedia.objects.all()
    serializer_class = UserMediaSerializer

    def get_object(self):
        return get_object_or_404(UserMedia, user=self.request.user)


class UserStatementDocumentsViewSet(BaseUserViewSet):
    queryset = UserStatementDocuments.objects.all()
    serializer_class = UserStatementDocumentsSerializer

    def get_object(self):
        return get_object_or_404(
            UserStatementDocuments, user=self.request.user
        )
