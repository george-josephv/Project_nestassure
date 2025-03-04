from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Extending Django User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('worker', 'Worker'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    housename = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    # Fix conflicts with default Django User model
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True
    )

    def __str__(self):
        return self.username


# Service Model
class Service(models.Model):
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.service_name

# Worker Model
class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    services = models.ManyToManyField(Service, related_name='workers')

    def __str__(self):
        return self.user.username


# Booking Model
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    booking_id = models.CharField(max_length=10, editable=False, null=True, blank=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='worker_bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_bookings')
    expected_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    extra_field = models.TextField(blank=True, null=True)  # Example extra field

    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username} - {self.worker.user.username}"


# Auto-generate Booking ID in format A10001
@receiver(pre_save, sender=Booking)
def generate_booking_id(sender, instance, **kwargs):
    if not instance.booking_id:
        last_booking = Booking.objects.order_by('-id').first()
        if last_booking and last_booking.booking_id.startswith('A'):
            last_id = int(last_booking.booking_id[1:])
            instance.booking_id = f"A{last_id + 1}"
        else:
            instance.booking_id = "A10001"


# Payment Model
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    total_hours = models.IntegerField(default=0)
    total_minutes = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def calculate_total(self):
        total_time_in_hours = self.total_hours + (self.total_minutes / 60)
        self.total_amount = total_time_in_hours * self.booking.service.rate_per_hour
        self.save()

    def __str__(self):
        return f"Payment {self.id} - {self.booking.user.username}"
