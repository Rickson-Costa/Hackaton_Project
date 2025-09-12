from django.urls import path
from django.contrib.auth import views as auth_views
from .views import auth_views as custom_auth_views, profile_views

app_name = 'accounts'

urlpatterns = [
    path('login/', custom_auth_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', custom_auth_views.RegisterView.as_view(), name='register'),

    path('profile/', profile_views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', profile_views.ProfileEditView.as_view(), name='profile_edit'),
    path('change-password/', profile_views.ChangePasswordView.as_view(), name='change_password'),

    path('users/', custom_auth_views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', custom_auth_views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', custom_auth_views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/toggle-status/', custom_auth_views.UserToggleStatusView.as_view(), name='user_toggle_status'),
]
