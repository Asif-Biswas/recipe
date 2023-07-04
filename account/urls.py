from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.handleLogin, name='login'),
    path('logout/', views.handleLogout, name='logout'),
    path('signup/', views.handleSignup, name='signup'),
    path('verify-email/', views.verifyEmail, name='verify_email'),
    path('verify-otp/', views.verifyOTP, name='verify_otp'),
    path('forget-password/', views.forgetPassword, name='forget_password'),
    path('reset-password/', views.resetPassword, name='reset_password'),

    # profile
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>', views.userProfile, name='profile'),
    path('edit-profile/', views.editProfile, name='edit_profile'),

]