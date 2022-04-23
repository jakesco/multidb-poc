"""Based on https://docs.djangoproject.com/en/4.0/topics/db/multi-db/"""

import threading

threadlocal = threading.local()


class RouterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        setattr(threadlocal, "TENANT_DB", request.user.username)
        response = self.get_response(request)
        setattr(threadlocal, "TENANT_DB", None)
        return response


def get_thread_local(attr, default=None):
    return getattr(threadlocal, attr, default)


class TenantRouter:
    """
    Primary router for tenant data. Ensures read/writes on core models
    go to user's personal database.
    """

    def db_for_read(self, model, **hints):
        """
        Reads go to user's database if core model.
        """
        if model._meta.app_label == "core":
            return get_thread_local("TENANT_DB")
        return None

    def db_for_write(self, model, **hints):
        """
        Writes go to user's database if core model.
        """
        if model._meta.app_label == "core":
            return get_thread_local("TENANT_DB")
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Only relations within the same database are allowed (default).
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure core models only end up in tenant databases.
        The rest end up in default database.
        """
        if db == 'default':
            return app_label != 'core'
        return app_label == 'core'


