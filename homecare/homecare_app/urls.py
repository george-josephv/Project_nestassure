from django.urls import path
from .import views
urlpatterns = [
    path('', views.landing_page, name='landing'),
    path("login/",views.login_view, name="login"),
    path("signup/",views.signup_view, name="signup"),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
     path('services/',views. servicelist, name='servicelist'),
     path('logout/',views.user_logout, name='logout'),
     path('workers/<int:service_id>/', views.worker_list, name='worker_list'),
]
