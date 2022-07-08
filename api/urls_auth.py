from django.urls import path

from api.views.auth import LoginUser, LogoutUser, RegisterUser, ChangeUserPassword


urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('change_password/', ChangeUserPassword.as_view(), name='change_password'),
]
