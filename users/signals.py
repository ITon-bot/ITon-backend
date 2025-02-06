from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from users.models import Experience


@receiver(post_save, sender=Experience)
@receiver(post_delete, sender=Experience)
def update_user_experience(sender, instance, **kwargs):
    """
    Обновляет total_experience пользователя при изменении записей в Experience.
    """
    user = instance.user
    user.calculate_total_experience()
