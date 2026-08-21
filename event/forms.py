from django import forms
from django.contrib.auth.models import User
from .models import Event, Category, Profile, EventMember, Budget
import datetime

# ============================================================
# EXISTING FORMS (Milestone 2)
# ============================================================

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'category', 'start_date', 'end_date', 'venue', 'description', 'status', 'image']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today()}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        today = datetime.date.today()

        if start_date and start_date < today:
            raise forms.ValidationError('Start date cannot be in the past.')

        if end_date and end_date < today:
            raise forms.ValidationError('End date cannot be in the past.')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('End date cannot be before start date.')

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


# ============================================================
# MILESTONE 3 — NEW FORMS
# ============================================================

class SignUpForm(forms.ModelForm):
    """Creates a real Django User account (student/attendee side)."""
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'email', 'username']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') and cleaned.get('confirm_password'):
            if cleaned['password'] != cleaned['confirm_password']:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned


class ProfileForm(forms.ModelForm):
    """Editable profile — photo, phone, bio (Item 1 of the improvement list)."""
    first_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ['photo', 'phone', 'bio']

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', user.first_name)
            user.email = self.cleaned_data.get('email', user.email)
            user.save()
        return profile


class ThemeForm(forms.ModelForm):
    """Theme customization panel (Image 2): font, primary color, sidebar color, size."""

    class Meta:
        model = Profile
        fields = ['font_family', 'primary_color', 'sidebar_color', 'font_size', 'dark_mode']
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'sidebar_color': forms.TextInput(attrs={'type': 'color'}),
            'font_size': forms.NumberInput(attrs={'min': 12, 'max': 22}),
        }


class EventMemberForm(forms.ModelForm):
    class Meta:
        model = EventMember
        fields = ['event', 'name', 'email', 'phone', 'role']


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['event', 'allocated_amount', 'spent_amount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
