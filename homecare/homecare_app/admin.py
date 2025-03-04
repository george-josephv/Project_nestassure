from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Service, Worker, Booking, Payment


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'phone_number', 'dob', 'blood_group', 'state', 'district', 'place', 'housename', 'profile_picture')}),
        ('Role & Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    
class BookingAdmin(admin.ModelAdmin):
    model = Booking
    list_display = ('user__email', 'booking_id',)
    search_fields = ('user__username', 'booking_id')

# Register models
admin.site.register(User)
admin.site.register(Service)
admin.site.register(Worker)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Payment)