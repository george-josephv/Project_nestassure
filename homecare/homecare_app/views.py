from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import BookingForm, EditProfileForm
from .models import User, Service, Worker, Booking, Payment
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date
from django.http import JsonResponse
from decimal import Decimal


def landing_page(request):
    return render(request, 'myapp/landingpage.html')  # No need to specify 'myapp/' in the template path



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == "worker":
                return redirect("worker_dashboard")  # Redirect workers
            else:
                return redirect("user_dashboard")  # Redirect users
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "myapp/login.html")  # Render login page if not authenticated

@login_required
def user_dashboard(request):
    return render(request, 'myapp/user_dashboard.html')
def user_logout(request):
    logout(request)
    return render(request, 'myapp/landingpage.html')

@login_required
def worker_dashboard(request):
    return render(request, 'myapp/workerdashome.html')
def worker_logout(request):
    logout(request)
    return render(request, 'myapp/landingpage.html')

#sign upp
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")
        role = request.POST.get("role")  # Get user role (worker or normal user)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        # Create and save the user
        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        login(request, user)  # Log in the user after signup

        # Redirect based on role
        if user.role == "worker":
            return redirect("login")
        else:
            return redirect("login")

    return render(request, "myapp/signup.html")



# servicelist
def servicelist(request):
    """View to display all available services."""
    services = Service.objects.all()
    return render(request, 'myapp/servicelist.html', {'services': services})

# workers_list
def worker_list(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    workers = Worker.objects.filter(services__id=service_id)  # Corrected query
    return render(request, 'myapp/worker_list.html', {'service': service, 'workers': workers})


@login_required
def book_worker(request, worker_id):
    worker = get_object_or_404(Worker, id=worker_id)

    # Get the first associated service (if exists)
    service = worker.services.first()

    if not service:  # Ensure the worker has a service before proceeding
        messages.error(request, "This worker has no associated services.")
        return redirect("worker_list")

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.worker = worker
            booking.service = service  # Assign the first service
            booking.save()

            messages.success(request, "Booking confirmed successfully!")
            return redirect("user_dashboard")  # Redirect after booking

    else:
        form = BookingForm()

    return render(request, "myapp/book_worker.html", {
        "worker": worker, 
        "form": form,
        "service": service  # Pass the service to the template
    })
   
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)  # Get only logged-in user's bookings

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        status = request.POST.get("status")  # "completed" or "pending"
        
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.status = status
        booking.save()
        
        messages.success(request, "Booking status updated successfully!")
        return redirect("my_bookings")  # Refresh page after submission

    return render(request, "myapp/my_bookings.html", {"bookings": bookings})

@login_required
def user_my_profile(request):
    return render(request, 'myapp/user_my_profile.html', {'user': request.user})

@login_required
def edit_user_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_my_profile')  # Redirect to profile page after saving
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'myapp/edit_user_profile.html', {'form': form})

# worker pages


@login_required
def worker_booking_list_view(request):
    worker = get_object_or_404(Worker, user=request.user)
    bookings = Booking.objects.filter(worker=worker).order_by('-id')

    # Get a list of expected dates for accepted bookings
    accepted_dates = list(Booking.objects.filter(worker=worker, status="accepted").values_list("expected_date", flat=True))

    context = {
        'bookings': bookings,
        'accepted_dates': accepted_dates
    }
    return render(request, 'myapp/worker_booking_list_view.html', context)

@login_required
def update_booking_status(request, booking_id, status):
    if request.method == "POST":
        try:
            booking = Booking.objects.get(id=booking_id, worker__user=request.user)
            if status in ["accepted", "rejected"]:
                booking.status = status
                booking.save()
                return JsonResponse({"success": True, "status": booking.status})
            else:
                return JsonResponse({"success": False, "error": "Invalid status"})
        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Booking not found"})
    
    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def worker_accepted_bookings(request):
    worker = request.user.worker_profile  # Get the logged-in worker
    accepted_bookings = Booking.objects.filter(worker=worker, status__in=['accepted', 'completed'])

    return render(request, 'myapp/worker_accepted_bookings.html', {'accepted_bookings': accepted_bookings})

# Payment form
@login_required

def payment_form(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        hours = int(request.POST.get("hours", 0))
        minutes = int(request.POST.get("minutes", 0))

        total_hours = Decimal(hours) + (Decimal(minutes) / Decimal(60))  # Convert to Decimal
        total_amount = total_hours * booking.service.rate_per_hour  # Now both are Decimal

        # Save payment details
        payment, created = Payment.objects.get_or_create(booking=booking)
        payment.total_hours = total_hours
        payment.total_amount = total_amount
        payment.is_paid = True  # Mark as paid if needed
        payment.save()

        return redirect("payment_success")  # Redirect to success page

    context = {
        "booking": booking,
        "rate_per_hour": booking.service.rate_per_hour,
        "hours_range": range(0, 24),
        "minutes_range": range(0, 60, 5),
    }
    return render(request, "myapp/payment_form.html", context)
