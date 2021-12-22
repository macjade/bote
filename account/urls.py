from django.urls import path
from . import views
app_name = "account"

urlpatterns=[
    path('register/', views.UserRegister.as_view(), name="user-register"),
    path('manageusername/', views.ManageUsername.as_view(), name="manage-username"),
    path('changeprofile/', views.ChangeProfileImage.as_view(), name="change-profile"),
    path('twoFA/', views.VerifyTwoFA.as_view(), name="verify-twofa"),
    path('new/twofatoken/', views.NewTwoFAToken.as_view(), name="generate-twofa"),
    path('forgotpassword/', views.SendPasswordResetEmail.as_view(), name="forgot-password"),
    path('resetpassword/', views.ResetPasswordView.as_view(), name="reset-password"),
    path('settings/', views.UserSettingView.as_view(), name="user-setting"),
    path('changepassword/', views.ChangePasswordView.as_view(), name="change-password"),
]