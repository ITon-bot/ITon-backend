from django.db import models

from users.models import User


class NotificationType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)


def __str__(self):
    return self.name


class NotificationSubscription(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    types = models.ManyToManyField(
        NotificationType,
        blank=True,
        related_name='subscribed_users'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - Notifications ({'active' if self.is_active else 'inactive'})"

    def save(self, *args, **kwargs):
        if not self.types.exists():
            self.is_active = False
        super().save(*args, **kwargs)
