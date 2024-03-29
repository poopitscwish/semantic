from django.apps import AppConfig
class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    def ready(self):
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in
        
        # Отключаем сигнал обновления last_login при входе пользователя
        user_logged_in.disconnect(update_last_login, dispatch_uid='update_last_login')