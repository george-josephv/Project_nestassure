from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import BookingForm, EditProfileForm
from .models import User, Service, Worker, Booking, Payment
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.http import JsonResponse
from decimal import Decimal
from django.utils.timezone import now

def landing_page(request):
    return render(request, 'myapp/landingpage.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == "worker":
                return redirect("worker_dashboard")
            else:
                return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "myapp/login.html")

@login_required
def user_dashboard(request):
    payments = Payment.objects.filter(booking__user=request.user)  # Get all payments for the logged-in user
    return render(request, 'myapp/user_dashboard.html', {'payments': payments})

def user_logout(request):
    logout(request)
    return render(request, 'myapp/landingpage.html')

@login_required
def worker_dashboard(request):
    return render(request, 'myapp/workerdashome.html')

def worker_logout(request):
    logout(request)
    return render(request, 'myapp/landingpage.html')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")
        role = request.POST.get("role")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        login(request, user)

        if user.role == "worker":
            return redirect("login")
        else:
            return redirect("login")

    return render(request, "myapp/signup.html")

def servicelist(request):
    services = Service.objects.all()
    return render(request, 'myapp/servicelist.html', {'services': services})

def worker_list(request,service_id):
    service_id = request.GET.get("service_id")
    services = Service.objects.all()

    if service_id:
        workers = Worker.objects.filter(services__id=service_id)
    else:
        workers = Worker.objects.all()

    return render(request, 'myapp/worker_list.html', {
        'services': services,
        'workers': workers,
        'selected_service_id': service_id
    })

@login_required
def book_worker(request, worker_id):
    worker = get_object_or_404(Worker, id=worker_id)
    service = worker.services.first()

    if not service:
        messages.error(request, "This worker has no associated services.")
        return redirect("worker_list")

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.worker = worker
            booking.service = service
            booking.save()
            messages.success(request, "Booking confirmed successfully!")
            return redirect("user_dashboard")

    else:
        form = BookingForm()

    return render(request, "myapp/book_worker.html", {
        "worker": worker, 
        "form": form,
        "service": service  
    })

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        status = request.POST.get("status")

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if booking.status == "accepted" and status == "completed":
            booking.status = "completed"
            booking.save()
            messages.success(request, "Booking marked as Completed!")
        else:
            messages.error(request, "Only Accepted bookings can be completed.")

        return redirect("my_bookings")

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
            return redirect('user_my_profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'myapp/edit_user_profile.html', {'form': form})

@login_required
def worker_booking_list_view(request):
    worker = get_object_or_404(Worker, user=request.user)
    bookings = Booking.objects.filter(worker=worker).order_by('-id')

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
    worker = request.user.worker_profile
    accepted_bookings = Booking.objects.filter(worker=worker, status__in=['accepted', 'completed'])

    # Get paid bookings from session
    paid_bookings = request.session.get("paid_bookings", [])

    return render(request, 'myapp/worker_accepted_bookings.html', {
        'accepted_bookings': accepted_bookings,
        'paid_bookings': paid_bookings
    })
    
@login_required
def worker_payment_form(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        total_hours = int(request.POST.get("hours", 0))
        total_minutes = int(request.POST.get("minutes", 0))

        # Convert total time into decimal hours
        total_time_in_hours = Decimal(total_hours) + (Decimal(total_minutes) / Decimal(60))

        # Convert rate_per_hour to Decimal
        rate_per_hour = Decimal(booking.service.rate_per_hour)

        # Calculate total amount with a 15% deduction
        total_amount = total_time_in_hours * rate_per_hour
        final_amount = total_amount * Decimal(0.85)  # Deduct 15%

        # Save payment details in the database
        payment, created = Payment.objects.get_or_create(booking=booking, defaults={"is_paid": False})
        payment.total_hours = total_hours
        payment.total_minutes = total_minutes
        payment.total_amount = final_amount
        payment.save()

        # 🔹 Store booking ID in session, preventing duplicates
        if "paid_bookings" not in request.session:
            request.session["paid_bookings"] = []
        
        if booking_id not in request.session["paid_bookings"]:
            request.session["paid_bookings"].append(booking_id)
            request.session.modified = True

        messages.success(request, f"Payment recorded! Final amount after 15% deduction: ₹{final_amount:.2f}")
        return redirect("worker_accepted_bookings")

    context = {
        "booking": booking,
        "rate_per_hour": booking.service.rate_per_hour,
        "hours_range": range(0, 25),  # Allow up to 24 hours
        "minutes_range": range(0, 60),  # Allow all minutes
    }
    return render(request, "myapp/worker_payment_form.html", context)

@login_required

def user_payment_processing_list(request):
    # Fetch bookings where payment is pending
    processing_bookings = Booking.objects.filter(status='completed', payment__isnull=False, payment__is_paid=False)

    return render(request, 'myapp/user_payment_processing_list.html', {'processing_bookings': processing_bookings})



@login_required
def user_payment_details(request, booking_id):
    payment = get_object_or_404(Payment, booking__id=booking_id)

    context = {
        'payment': payment,
        'booking_id': payment.booking.id,  # Default ID
        'service_booked': payment.booking.service.service_name,
        'worker_name': payment.booking.worker.user.username,
        'worker_email': payment.booking.worker.user.email,
        'address': f"{payment.booking.user.state}, {payment.booking.user.district}, {payment.booking.user.place}, {payment.booking.user.housename}",
        'expected_date': payment.booking.expected_date,
        'work_status': payment.booking.status,
        'rate_per_hour': payment.booking.service.rate_per_hour,
        'total_time': f"{payment.total_hours} hours {payment.total_minutes} minutes",
        'total_amount': payment.total_amount,
        'is_paid': payment.is_paid,  # Check if the payment is completed
    }

    return render(request, 'myapp/user_payment_details.html', context)

@csrf_exempt
def mark_payment_done(request, booking_id):
    if request.method == "POST":
        payment = get_object_or_404(Payment, booking__id=booking_id)
        payment.is_paid = True
        payment.save()
        return JsonResponse({"message": "Payment marked as done", "status": "paid"})

# histort of payment



@login_required
def payment_history(request):
    paid_payments = Payment.objects.filter(is_paid=True).order_by('id')
    current_date = now().date()

    # Redirect to "payment-processing/" if no paid payments exist
    if not paid_payments:
        return redirect('user_payment_processing_list')  # Replace with your actual URL name

    return render(request, 'myapp/payment_history.html', {
        'paid_payments': paid_payments,
        'current_date': current_date
    })