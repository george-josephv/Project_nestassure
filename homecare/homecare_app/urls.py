from django.urls import path
from .import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('worker_dash/', views.worker_dashboard, name='worker_dashboard'),
    path('services/', views.servicelist, name='servicelist'),
    
    # Fixed logout paths
    path('logout/', views.user_logout, name='user_logout'),
    path('worker_logout/', views.worker_logout, name='worker_logout'),

    path('workers/<int:service_id>/', views.worker_list, name='worker_list'),
    
    # 1-3-25
    path('book_worker/<int:worker_id>/<str:service>/', views.book_worker, name='book_worker'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('profile/', views.user_my_profile, name='user_my_profile'),
    path('profile/edit/', views.edit_user_profile, name='edit_user_profile'),
    
    # Worker
    path('worker/bookings/', views.worker_booking_list_view, name='worker_bookings'),
    path('worker/bookings/update/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    path('worker/accepted-bookings/', views.worker_accepted_bookings, name='worker_accepted_bookings'),
    path('worker/payment/<int:booking_id>/', views.worker_payment_form, name='worker_payment_form'),
    
    # Payment
    path('payment-processing/', views.user_payment_processing_list, name='user_payment_processing_list'),
    path('payment/details/<int:booking_id>/', views.user_payment_details, name='user_payment_details'),
    path('payment/mark/<int:booking_id>/', views.mark_payment_done, name='mark_payment_done'),
    path('payment-history/', views.payment_history, name='payment_history'),
]
