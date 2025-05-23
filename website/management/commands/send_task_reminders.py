import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from website.models import Task, Notification, User, UserProfile

class Command(BaseCommand):
    help = 'Scans for tasks that are due soon or overdue and sends notifications and emails.'

    def handle(self, *args, **options):
        now = timezone.now()
        due_soon_threshold = now + datetime.timedelta(days=1) # Tasks due in the next 24 hours
        one_day_ago = now - datetime.timedelta(days=1)

        # Get tasks that are not completed and are due within the threshold (including overdue)
        upcoming_or_overdue_tasks = Task.objects.filter(
            is_completed=False,
            due_date__lte=due_soon_threshold
        )

        if not upcoming_or_overdue_tasks.exists():
            self.stdout.write(self.style.NOTICE('No upcoming or overdue tasks found to notify for.'))
            return

        notified_count = 0
        for task in upcoming_or_overdue_tasks:
            if not task.user: # Should not happen if data is clean, but good to check
                self.stdout.write(self.style.WARNING(f'Task "{task.title}" (ID: {task.id}) has no assigned user. Skipping.'))
                continue

            notification_title = f"Task Reminder: {task.title}"
            
            if task.due_date < now:
                notification_message = f"Your task '{task.title}' was due on {task.due_date.strftime('%Y-%m-%d %H:%M')} and is overdue."
            else:
                notification_message = f"Your task '{task.title}' is due on {task.due_date.strftime('%Y-%m-%d %H:%M')}."

            # Construct link to the record page where the task is displayed
            # Assuming 'record' is the name of the URL pattern for customer_record view
            try:
                task_link_url = reverse('record', args=[task.record.id])
                # Optionally, if you can identify tasks by an HTML anchor:
                # task_link_url += f"#task-{task.id}" 
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Could not generate link for task {task.id}: {e}'))
                task_link_url = None # Or a generic link

            # Check for existing recent notification for this task to avoid duplicates
            # This check is simplified: it looks for a notification with a similar title for the same user
            # and task record within the last day. A more robust check might involve a direct link to the task in Notification model.
            similar_notification_exists = Notification.objects.filter(
                user=task.user,
                title__icontains=task.title, # A bit lenient, could be more specific
                link__icontains=reverse('record', args=[task.record.id]), # Check if link points to same record
                created_at__gte=one_day_ago 
            ).exists()

            if not similar_notification_exists:
                # Create In-App Notification
                Notification.objects.create(
                    user=task.user,
                    title=notification_title,
                    message=notification_message,
                    link=task_link_url
                )
                self.stdout.write(self.style.SUCCESS(f'In-app notification created for task: "{task.title}" for {task.user.username}'))
                notified_count += 1

                # Send Email Notification if user has opted-in
                try:
                    # Ensure user profile exists; it should due to signals, but defensive check
                    user_profile = task.user.profile
                    if user_profile.receive_email_notifications:
                        if task.user.email:
                            email_subject = f"[CRM Task Reminder] {task.title}"
                            email_body = f"Hello {task.user.first_name or task.user.username},\n\n"
                            email_body += f"{notification_message}\n\n"
                            if task_link_url:
                                # Attempt to build a full URL if settings.SITE_URL is defined
                                site_url = getattr(settings, 'SITE_URL', '')
                                full_task_link = site_url + task_link_url if site_url else task_link_url
                                email_body += f"You can view the task details here: {full_task_link}\n\n"
                            email_body += "Regards,\nYour CRM System"
                            
                            send_mail(
                                email_subject,
                                email_body,
                                settings.DEFAULT_FROM_EMAIL,
                                [task.user.email],
                                fail_silently=False,
                            )
                            self.stdout.write(self.style.SUCCESS(f'Email sent for task: "{task.title}" to {task.user.email}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'User {task.user.username} has no email address. Cannot send email reminder.'))
                    else:
                        self.stdout.write(self.style.NOTICE(f'User {task.user.username} opted out of email notifications for task: "{task.title}". Skipping email.'))
                except UserProfile.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'UserProfile not found for user {task.user.username}. Cannot check email preferences.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to send email for task "{task.title}" to {task.user.username}: {e}'))
            
            else:
                self.stdout.write(self.style.NOTICE(f'Recent in-app notification already exists for task: "{task.title}" for user {task.user.username}. Skipping in-app and email.'))

        if notified_count > 0: # This now counts in-app notifications primarily
            self.stdout.write(self.style.SUCCESS(f'Successfully processed {notified_count} tasks for potential notifications/emails.'))
        else:
            self.stdout.write(self.style.NOTICE('No new tasks required in-app notifications (possibly all tasks already had recent reminders).'))
