from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update UserProfile when a User instance is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Ensure profile exists, for example, if users were created before this signal
        # or if the profile was somehow deleted.
        profile, new_profile_created = UserProfile.objects.get_or_create(user=instance)
        if not new_profile_created:
            profile.save() # Call save to ensure any potential updates on profile are triggered
        # If you had fields on UserProfile that needed to be updated based on User changes,
        # you would do it here before profile.save().
        # For now, just ensuring it exists and saving is enough.
        # A more direct approach if only caring about existing profiles:
        # if hasattr(instance, 'profile'):
        #    instance.profile.save()
        # else:
        #    UserProfile.objects.create(user=instance) # For users created before this signal was active
    
    # A simpler version ensuring profile exists and is saved:
    # try:
    #     instance.profile.save()
    # except UserProfile.DoesNotExist:
    #     UserProfile.objects.create(user=instance)
