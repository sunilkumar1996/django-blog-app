from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="register_view"),
    path('login/', views.LoginView.as_view(), name="login_view"),
    path('logout/', views.Logout.as_view(), name="logout"),
]
