from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Record, Note, Task, RecordFile, Notification, UserProfile

# Register your other models here as before
admin.site.register(Record)
admin.site.register(Note)
admin.site.register(Task)
admin.site.register(RecordFile)
admin.site.register(Notification)

# Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Settings'
    fields = ('receive_email_notifications',) # Specify fields to show

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Optionally, if you want a separate admin page for UserProfile as well
# admin.site.register(UserProfile)
