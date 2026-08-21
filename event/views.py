from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse

from .models import (
    Event, Category, Profile, EventMember,
    Registration, Wishlist, Budget, Notification,
)
from .forms import (
    EventForm, CategoryForm, SignUpForm, ProfileForm,
    ThemeForm, EventMemberForm, BudgetForm,
)


def staff_required(user):
    return user.is_authenticated and user.is_staff


# ============================================================
# Home / Auth
# ============================================================

def home_view(request):
    upcoming_events = Event.objects.filter(status='active').order_by('start_date')[:6]
    return render(request, 'home/index.html', {'upcoming_events': upcoming_events})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'authentication/login.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            profile = user.profile
            profile.phone = form.cleaned_data.get('phone', '')
            profile.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please fix the errors below and try again.')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ============================================================
# Admin Dashboard
# ============================================================

@login_required(login_url='login')
def dashboard_view(request):
    events = Event.objects.all().order_by('-created_at')[:8]
    context = {
        'events': events,
        'total_events': Event.objects.count(),
        'total_categories': Category.objects.count(),
        'total_completed': Event.objects.filter(status='completed').count(),
        'total_members': Registration.objects.filter(status='attending').count(),
    }
    return render(request, 'dashboard/dashboard.html', context)


# ============================================================
# User Panel
# ============================================================

@login_required(login_url='login')
def user_dashboard_view(request):
    today = timezone.now().date()
    available_events = Event.objects.filter(status='active').order_by('start_date')
    upcoming_events = Event.objects.filter(status='active', start_date__gt=today).order_by('start_date')[:5]

    my_registration_event_ids = set(
        Registration.objects.filter(user=request.user, status='attending').values_list('event_id', flat=True)
    )
    my_wishlist_event_ids = set(
        Wishlist.objects.filter(user=request.user).values_list('event_id', flat=True)
    )

    context = {
        'available_events': available_events,
        'upcoming_events': upcoming_events,
        'my_registration_event_ids': my_registration_event_ids,
        'my_wishlist_event_ids': my_wishlist_event_ids,
    }
    return render(request, 'user_panel/user-dashboard.html', context)


# ============================================================
# Event views
# ============================================================

@login_required(login_url='login')
def event_list_view(request):
    events = Event.objects.all()
    query = request.GET.get('q')
    if query:
        events = events.filter(name__icontains=query)
    return render(request, 'event/event-list.html', {'events': events, 'query': query or ''})


@login_required(login_url='login')
def create_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully')
            return redirect('event_list')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = EventForm()

    categories = Category.objects.all()
    return render(request, 'event/create-event.html', {'form': form, 'categories': categories})


@login_required(login_url='login')
def edit_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully')
            return redirect('event_list')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = EventForm(instance=event)  # ← FIX: load existing data on GET

    categories = Category.objects.all()
    return render(request, 'event/edit-event.html', {'event': event, 'categories': categories, 'form': form})


@login_required(login_url='login')
def event_details_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registrations_count = event.registrations.filter(status='attending').count()
    return render(request, 'event/event-details.html', {
        'event': event,
        'registrations_count': registrations_count,
    })


@login_required(login_url='login')
def delete_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted')
        return redirect('event_list')
    return render(request, 'event/delete-event.html', {'event': event})


@login_required(login_url='login')
def complete_event_list_view(request):
    events = Event.objects.filter(status='completed').order_by('-end_date')
    return render(request, 'event/complete-event-list.html', {'events': events})


# ============================================================
# Category views
# ============================================================

@login_required(login_url='login')
def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'category/category-list.html', {'categories': categories})


@login_required(login_url='login')
def create_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully')
            return redirect('category_list')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = CategoryForm()
    return render(request, 'category/create-category.html', {'form': form})


@login_required(login_url='login')
def edit_category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('category_list')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = CategoryForm(instance=category)  # ← FIX: load existing data on GET

    return render(request, 'category/edit-category.html', {'category': category, 'form': form})


@login_required(login_url='login')
def category_details_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.event_count = Event.objects.filter(category=category).count()
    return render(request, 'category/category-details.html', {'category': category})


@login_required(login_url='login')
def delete_category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted')
        return redirect('category_list')
    return render(request, 'category/delete-category.html', {'category': category})


# ============================================================
# Profile & Theme Settings
# ============================================================

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'profile/my-profile.html', {'profile': request.user.profile})


@login_required(login_url='login')
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(
            request.POST, request.FILES, instance=profile,
            initial={'first_name': request.user.first_name, 'email': request.user.email},
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = ProfileForm(
            instance=profile,
            initial={'first_name': request.user.first_name, 'email': request.user.email},
        )
    return render(request, 'profile/edit-profile.html', {'form': form})


@login_required(login_url='login')
def theme_settings_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ThemeForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Theme updated')
            return redirect(request.META.get('HTTP_REFERER') or 'theme_settings')
    else:
        form = ThemeForm(instance=profile)
    return render(request, 'settings/theme-settings.html', {'form': form, 'profile': profile})


@login_required(login_url='login')
def reset_theme_view(request):
    profile = request.user.profile
    profile.font_family = 'Poppins'
    profile.primary_color = '#3949ab'
    profile.sidebar_color = '#17203a'
    profile.font_size = 16
    profile.dark_mode = False
    profile.save()
    messages.success(request, 'Theme reset to default')
    return redirect(request.META.get('HTTP_REFERER') or 'theme_settings')


@login_required(login_url='login')
def toggle_dark_mode_view(request):
    profile = request.user.profile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
    return redirect(next_url)


# ============================================================
# Event Members
# ============================================================

@login_required(login_url='login')
def event_member_list_view(request):
    members = EventMember.objects.select_related('event').all().order_by('-added_at')
    return render(request, 'members/member-list.html', {'members': members})


@login_required(login_url='login')
def add_event_member_view(request):
    if request.method == 'POST':
        form = EventMemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event member added')
            return redirect('event_member_list')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = EventMemberForm()
    return render(request, 'members/add-member.html', {'form': form})


@login_required(login_url='login')
def delete_event_member_view(request, pk):
    member = get_object_or_404(EventMember, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Member removed')
    return redirect('event_member_list')


# ============================================================
# Registration / Tickets
# ============================================================

@login_required(login_url='login')
def register_for_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registration, created = Registration.objects.get_or_create(
        event=event, user=request.user, defaults={'status': 'attending'}
    )
    if not created and registration.status == 'cancelled':
        registration.status = 'attending'
        registration.save()
    if created:
        messages.success(request, f'You are registered for {event.name}!')
    else:
        messages.info(request, "You're already registered for this event.")
    return redirect('view_ticket', ticket_id=registration.ticket_id)


@login_required(login_url='login')
def view_ticket_view(request, ticket_id):
    registration = get_object_or_404(Registration, ticket_id=ticket_id)
    if registration.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect('user_dashboard')
    return render(request, 'registration/ticket.html', {'registration': registration})


@login_required(login_url='login')
def my_tickets_view(request):
    registrations = Registration.objects.filter(user=request.user).select_related('event')
    return render(request, 'registration/my-tickets.html', {'registrations': registrations})


@login_required(login_url='login')
def download_ticket_pdf_view(request, ticket_id):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A5
    from reportlab.lib.units import mm

    registration = get_object_or_404(Registration, ticket_id=ticket_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{registration.ticket_id}.pdf"'

    c = canvas.Canvas(response, pagesize=A5)
    width, height = A5

    c.setFillColorRGB(0.09, 0.13, 0.23)
    c.rect(0, height - 30 * mm, width, 30 * mm, fill=True, stroke=False)
    c.setFillColorRGB(1, 1, 1)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(15 * mm, height - 18 * mm, registration.event.name)
    c.setFont('Helvetica', 10)
    c.drawString(15 * mm, height - 25 * mm, f"Ticket: {registration.ticket_id}")

    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica', 11)
    y = height - 42 * mm
    fields = [
        ('Participant', registration.user.get_full_name() or registration.user.username),
        ('Email', registration.user.email or '-'),
        ('Venue', registration.event.venue),
        ('Event Date', str(registration.event.start_date)),
        ('Status', registration.get_status_display()),
    ]
    for label, value in fields:
        c.setFont('Helvetica-Bold', 10)
        c.drawString(15 * mm, y, f"{label}:")
        c.setFont('Helvetica', 10)
        c.drawString(45 * mm, y, str(value))
        y -= 7 * mm

    if registration.qr_code:
        try:
            c.drawImage(registration.qr_code.path, width - 55 * mm, height - 95 * mm,
                        width=40 * mm, height=40 * mm)
        except Exception:
            pass

    c.setFont('Helvetica-Oblique', 8)
    c.drawString(15 * mm, 10 * mm, f"Verification token: {registration.verification_token}")

    c.showPage()
    c.save()
    return response


@login_required(login_url='login')
def admin_registration_list_view(request):
    registrations = Registration.objects.select_related('event', 'user').all()
    event_filter = request.GET.get('event')
    if event_filter:
        registrations = registrations.filter(event_id=event_filter)
    return render(request, 'registration/join-event-list.html', {
        'registrations': registrations,
        'events': Event.objects.all(),
        'selected_event': event_filter,
    })


# ============================================================
# Wishlist
# ============================================================

@login_required(login_url='login')
def toggle_wishlist_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    wishlist_item, created = Wishlist.objects.get_or_create(event=event, user=request.user)
    if not created:
        wishlist_item.delete()
        messages.info(request, f'Removed {event.name} from your wishlist')
    else:
        messages.success(request, f'Added {event.name} to your wishlist')
    return redirect(request.META.get('HTTP_REFERER', 'user_dashboard'))


@login_required(login_url='login')
def admin_wishlist_list_view(request):
    wishlist_items = Wishlist.objects.select_related('event', 'user').all()
    return render(request, 'wishlist/event-wish-list.html', {'wishlist_items': wishlist_items})


@login_required(login_url='login')
def add_wishlist_user_view(request):
    if request.method == 'POST':
        event_id = request.POST.get('event')
        username = request.POST.get('username')
        event = get_object_or_404(Event, pk=event_id)
        user = User.objects.filter(username=username).first()
        if not user:
            messages.error(request, f'No user found with username "{username}"')
        else:
            _, created = Wishlist.objects.get_or_create(event=event, user=user)
            if created:
                messages.success(request, f'Added {user.username} to the wishlist for {event.name}')
            else:
                messages.info(request, f'{user.username} is already on the wishlist for {event.name}')
        return redirect('admin_wishlist_list')
    return render(request, 'wishlist/add-wish-user.html', {'events': Event.objects.all()})


# ============================================================
# Attendance / QR Verification
# ============================================================

def _decode_qr_from_image(uploaded_file):
    import cv2
    import numpy as np
    uploaded_file.seek(0)
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        return None
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data or None

@login_required(login_url='login')
def scan_qr_view(request):
    result = None
    if request.method == 'POST':
        registration = None

        if 'qr_image' in request.FILES:
            try:
                token = _decode_qr_from_image(request.FILES['qr_image'])
            except ImportError:
                messages.error(request, 'opencv-python-headless is not installed.')
                return redirect('scan_qr')
            if token:
                registration = Registration.objects.filter(verification_token=token).first()
            if not registration:
                result = {'success': False, 'message': 'Could not read a valid ticket from that image.'}

        elif request.POST.get('ticket_token'):
            raw = request.POST.get('ticket_token').strip()
            registration = (
                Registration.objects.filter(verification_token=raw).first()
                or Registration.objects.filter(ticket_id__iexact=raw).first()
            )
            if not registration:
                result = {'success': False, 'message': f'No ticket found matching "{raw}".'}

        if registration:
            if registration.status == 'cancelled':
                result = {'success': False, 'message': 'This ticket has been cancelled.'}
            elif registration.checked_in:
                result = {'success': False, 'message': f'Ticket already used! Checked in at {registration.checked_in_at}.'}
            else:
                registration.checked_in = True
                registration.checked_in_at = timezone.now()
                registration.save()
                result = {'success': True, 'registration': registration}

    return render(request, 'attendance/scan-qr.html', {'result': result})



# ============================================================
# Finance / Budget Management
# ============================================================

@login_required(login_url='login')
def budget_list_view(request):
    budgets = Budget.objects.select_related('event').all()
    search = request.GET.get('q')
    if search:
        budgets = budgets.filter(event__name__icontains=search)
    totals = budgets.aggregate(
        total_allocated=Sum('allocated_amount'),
        total_spent=Sum('spent_amount'),
    )
    return render(request, 'finance/budget-list.html', {
        'budgets': budgets,
        'search': search or '',
        'total_allocated': totals['total_allocated'] or 0,
        'total_spent': totals['total_spent'] or 0,
    })


@login_required(login_url='login')
def create_budget_view(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget created')
            return redirect('budget_list')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = BudgetForm()
    return render(request, 'finance/create-budget.html', {'form': form})


@login_required(login_url='login')
def edit_budget_view(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated')
            return redirect('budget_list')
        else:
            messages.error(request, 'Please check the form and try again')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'finance/edit-budget.html', {'form': form, 'budget': budget})


@login_required(login_url='login')
def delete_budget_view(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted')
    return redirect('budget_list')


@login_required(login_url='login')
def finance_analysis_view(request):
    budgets = Budget.objects.select_related('event').all()
    chart_labels = [b.event.name for b in budgets]
    chart_allocated = [float(b.allocated_amount) for b in budgets]
    chart_spent = [float(b.spent_amount) for b in budgets]
    totals = budgets.aggregate(
        total_allocated=Sum('allocated_amount'),
        total_spent=Sum('spent_amount'),
    )
    return render(request, 'finance/finance-analysis.html', {
        'chart_labels': chart_labels,
        'chart_allocated': chart_allocated,
        'chart_spent': chart_spent,
        'total_allocated': totals['total_allocated'] or 0,
        'total_spent': totals['total_spent'] or 0,
        'budgets': budgets,
    })


# ============================================================
# Notifications
# ============================================================

@login_required(login_url='login')
def notifications_list_view(request):
    notifications = Notification.objects.all()
    Notification.objects.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/notification-list.html', {'notifications': notifications})


@login_required(login_url='login')
def mark_notifications_read_view(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

# chatbot_view
import json as _json

@login_required(login_url='login')
def chatbot_view(request):
    if request.method == 'POST':
        try:
            from google import genai
            from django.conf import settings as django_settings

            data = _json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'reply': 'Please type a message.'})

            client = genai.Client(api_key=django_settings.GEMINI_API_KEY)

            prompt = f"""You are a helpful assistant for an Event Registration Platform.
Help users with questions about events, registration, tickets, and the platform.
Keep answers short and friendly.

User: {user_message}"""

            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            return JsonResponse({'reply': response.text})

        except Exception as e:
            # AFTER (temporary - just for debugging)
            return JsonResponse({'reply': f'DEBUG ERROR: {str(e)}'})

    return JsonResponse({'error': 'Invalid request'}, status=400)