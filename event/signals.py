from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Profile, Event, Registration, Notification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Every new User automatically gets a Profile (photo + theme prefs)."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Event)
def notify_event_created_or_completed(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            notif_type='event_created',
            title='New Event Created',
            message=f'"{instance.name}" has been created.',
            event=instance,
        )
    elif instance.status == 'completed':
        # Avoid duplicate "completed" notifications piling up on every save
        already_notified = Notification.objects.filter(
            event=instance, notif_type='event_completed'
        ).exists()
        if not already_notified:
            Notification.objects.create(
                notif_type='event_completed',
                title='Event Completed',
                message=f'"{instance.name}" has been marked completed.',
                event=instance,
            )


@receiver(post_save, sender=Registration)
def notify_new_registration(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            notif_type='registration',
            title='New Event Registration',
            message=f'{instance.user.username} registered for {instance.event.name}.',
            event=instance.event,
        )
