from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class RetrieveViewSet(mixins.RetrieveModelMixin,
                      GenericViewSet):
    """Миксин, разрешающий методы чтения только у конкретного юзера."""
    pass


class RetrieveUpdateViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericViewSet):
    """Миксин, разрешающий методы чтения только у конкретного юзера."""
    pass


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


class CreateListRetrieveDestroyViewSet(mixins.CreateModelMixin,
                                       mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin,
                                       mixins.DestroyModelMixin,
                                       GenericViewSet):
    """
    Миксин для эндпоинта /events/<event_pk>/applications/
    разрешающий все методы, кроме обновления.
    """
    pass


class ListRetrieveDestroyViewSet(mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.DestroyModelMixin,
                                 GenericViewSet):
    """
    Миксин для эндпоинта /events/<event_pk>/participants/
    разрешающий только методы чтения и удаления.
    """
    pass


class RetrieveUpdateViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericViewSet):
    """
    Миксин для эндпоинта /events/<event_pk>/answers/
    разрешающий только методы чтения(retrieve) и обновления.
    """
    pass


class CreateRetrieveUpdateViewSet(mixins.CreateModelMixin,
                                  mixins.RetrieveModelMixin,
                                  mixins.UpdateModelMixin,
                                  GenericViewSet):
    """
    Миксин для эндпоинта /events/<event_pk>/user_documents/
    разрешающий только все методы, кроме чтения (list) и удаления.
    """
    pass
