from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class ListRetrieveViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """Миксин, разрешающий только методы чтения."""
    pass


class ListRetrieveUpdateViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                mixins.UpdateModelMixin,
                                GenericViewSet):
    """
    Миксин для эндпоинта /user, разрешающий только методы чтения и обновления.
    """
    pass


class CreateViewSet(mixins.CreateModelMixin,
                    GenericViewSet):
    pass


class CreateDeleteViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    pass