from .models import Notification


def notifications_processor(request):
    """Makes the notification bell + dropdown available on every page."""
    if request.user.is_authenticated:
        recent = Notification.objects.all()[:8]
        unread_count = Notification.objects.filter(is_read=False).count()
        return {
            'nav_notifications': recent,
            'nav_unread_count': unread_count,
        }
    return {'nav_notifications': [], 'nav_unread_count': 0}


def theme_processor(request):
    """Makes the logged-in user's saved theme (Image 2) available everywhere,
    so the navbar/sidebar/footer colors stay consistent on every page."""
    defaults = {
        'theme_font_family': 'Poppins',
        'theme_primary_color': '#3949ab',
        'theme_sidebar_color': '#17203a',
        'theme_font_size': 16,
        'theme_dark_mode': False,
    }
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        return {
            'theme_font_family': profile.font_family,
            'theme_primary_color': profile.primary_color,
            'theme_sidebar_color': profile.sidebar_color,
            'theme_font_size': profile.font_size,
            'theme_dark_mode': profile.dark_mode,
        }
    return defaults
