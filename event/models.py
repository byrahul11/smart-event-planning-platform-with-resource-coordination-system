import uuid
from io import BytesIO

from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile


# ============================================================
# EXISTING MODELS (Milestone 2) — unchanged, kept as-is
# ============================================================

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # --- MILESTONE 3 additions to Event ---
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ============================================================
# MILESTONE 3 — NEW MODELS
# ============================================================

class Profile(models.Model):
    """Extends the built-in User with a photo + theme preferences.
    One Profile per User, created automatically on signup (see signals.py)."""

    FONT_CHOICES = [
        ('Poppins', 'Poppins'),
        ('Roboto', 'Roboto'),
        ('Inter', 'Inter'),
        ('Arial', 'Arial'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    # ---- Theme Settings (see Image 2: Font Family, Primary/Sidebar color, Font size) ----
    font_family = models.CharField(max_length=30, choices=FONT_CHOICES, default='Poppins')
    primary_color = models.CharField(max_length=7, default='#3949ab')   # topbar / buttons
    sidebar_color = models.CharField(max_length=7, default='#17203a')   # sidebar
    font_size = models.PositiveSmallIntegerField(default=16)            # px
    dark_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class EventMember(models.Model):
    """Organizing-team members assigned to run an event (not attendees)."""

    ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('coordinator', 'Coordinator'),
        ('volunteer', 'Volunteer'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='volunteer')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_role_display()}) - {self.event.name}"


class Registration(models.Model):
    """A user joining/registering for an event. Generates a unique ticket + QR code."""

    STATUS_CHOICES = [
        ('attending', 'Attending'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    ticket_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    verification_token = models.CharField(max_length=64, unique=True, editable=False, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='attending')
    registered_at = models.DateTimeField(auto_now_add=True)
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.ticket_id} - {self.user.username} - {self.event.name}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.ticket_id:
            self.ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        if not self.verification_token:
            self.verification_token = uuid.uuid4().hex
        super().save(*args, **kwargs)
        if is_new and not self.qr_code:
            self._generate_qr_code()

    def _generate_qr_code(self):
        """Encodes the verification_token into a QR image and attaches it."""
        import qrcode
        qr_img = qrcode.make(self.verification_token)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        filename = f"{self.ticket_id}.png"
        # save=False avoids infinite save() recursion; update() writes the field directly
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        Registration.objects.filter(pk=self.pk).update(qr_code=self.qr_code.name)


class Wishlist(models.Model):
    """A user marking interest in an event ('Event Wish List')."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='wishlisted_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} wishlisted {self.event.name}"


class Budget(models.Model):
    """Finance module: budget allocated to a single event."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='budgets')
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def remaining_amount(self):
        return self.allocated_amount - self.spent_amount

    @property
    def percent_used(self):
        if self.allocated_amount:
            return round((self.spent_amount / self.allocated_amount) * 100, 1)
        return 0

    def __str__(self):
        return f"Budget for {self.event.name}"


class Notification(models.Model):
    """Powers the navbar bell dropdown (Image 4): event created, registrations, completions."""

    TYPE_CHOICES = [
        ('event_created', 'Event Created'),
        ('registration', 'New Registration'),
        ('event_completed', 'Event Completed'),
        ('wishlist', 'Wishlist'),
    ]

    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# ============================================================
# Admin Inbox (student ↔ admin messaging)
# ============================================================

class SupportMessage(models.Model):
    """One row = one message. `thread_user` is always the student side of
    the conversation — so a whole thread is just: filter(thread_user=X).
    `sender` tells us whether the student or an admin wrote this particular message."""

    thread_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_threads')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_support_messages')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} in thread({self.thread_user.username})"