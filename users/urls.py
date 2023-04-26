from django.urls import path

from . import views

urlpatterns = [
    # path('users', views.users), # Deprecated.
    path('register', views.register),
    path('login', views.login),
    path('user', views.AuthenticatedUser.as_view()),
    path('permissions', views.PermissionApiView.as_view()),
    path('logout', views.logout),

    # those all belongs to the RolesViewSet method!
    path('roles', views.RoleViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),
    path('roles/<str:pk>', views.RoleViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),  # End of RolesViewSet path's.

    path('users', views.UserGenericAPIView.as_view()),
    path('users/info', views.ProfileInfoAPIView.as_view()),
    path('users/password', views.ProfilePasswordAPIView.as_view()),
    # this is the most general so it has to be last!
    path('users/<str:pk>', views.UserGenericAPIView.as_view()),

]
