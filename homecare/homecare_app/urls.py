from django.urls import path
from .import views
urlpatterns = [
    path('', views.landing_page, name='landing'),
    path("login/",views.login_view, name="login"),
    path("signup/",views.signup_view, name="signup"),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('worker_dash/', views.worker_dashboard, name='worker_dashboard'),
    path('services/',views. servicelist, name='servicelist'),
    path('logout/',views.user_logout, name='logout'),
    path('logout/',views.worker_logout, name='logout'),
    path('workers/<int:service_id>/', views.worker_list, name='worker_list'),
    # 1-3-25
    path('book_worker/<int:worker_id>/',views. book_worker, name='book_worker')
]
