from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(init_permissions, sender=self)

def init_permissions(sender, **kwargs):
    """
    Wrapper to call the management command after migrations
    """
    from django.core.management import call_command
    # Run only for the default database being migrated
    db = kwargs.get('using', 'default')
    try:
        print(f"Post-migrate: Inicializando permisos en '{db}'...")
        call_command('init_role_permissions', database=db)
    except Exception as e:
        print(f"Error en post-migrate init_permissions: {e}")
