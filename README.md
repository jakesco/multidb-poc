# Multi-tenant Proof of Concept

Proof of concept for multiple tenant databases in Django.

By default, the fixtures create 2 users **tenant1** and **tenant2** both with password=**password**.

## Getting Started

After creating and activating a python virtual environment, install dependencies and run the `refre.sh` script.

```bash
> python -m venv venv
> source venv/bin/activate
(venv) > pip install -r requirements.txt
(venv) > bash refre.sh
(venv) > python manage.py runserver
```
You can then navigate to `http://127.0.0.1:8000`.

## Database Routers

The idea for this project was to have tenant data stored in separate databases with query routing done
automatically based on the logged-in user. 
Normally one would need to specify the target database with the `using` modifier on a queryset.

```python
Item.objects.using('tenant1').all()
```

This query would then be routed to the database labeled `tenant1` in settings. 
By exposing the logged-in user to Django's database router framework, we can elide the `using` modifier
and have queries routed to the appropriate tenant database.

```python
Item.objects.all()
```
will be routed to the correct tenant database for the duration of a request.

The primary code to make this work is in `multidb-poc/core/routers.py`. 
There are two components, a `RouterMiddleware` and `TenantRouter`. 
The `RouterMiddleware` is responsible for exposing the user object to thread local variables.

```python
import threading

threadlocal = threading.local()


class RouterMiddleware:
    """Middleware to expose the logged-in username to thread local."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set TENANT_DB in threadlocal to username.
        setattr(threadlocal, "TENANT_DB", request.user.username)
        response = self.get_response(request)
        # Clear TENANT_DB after request is processed.
        setattr(threadlocal, "TENANT_DB", None)
        return response


def get_thread_local(attr, default=None):
    return getattr(threadlocal, attr, default)
```

The `TenantRouter` ensures queries are routed to the correct database.

```python
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
```
Note `allow_migrate` ensures only core models are stored in the tenant databases during migration.
All other application models (auth, sessions, etc.) are stored in and retrieved from the default database.

## References

* https://docs.djangoproject.com/en/4.0/topics/db/multi-db/
* https://docs.djangoproject.com/en/4.0/topics/http/middleware/
* https://stackoverflow.com/questions/39354715/django-database-routing-based-on-current-user-logged-in
* https://adriennedomingus.com/blog/django-databases-and-decorators
* https://simpleisbetterthancomplex.com/tutorial/2016/07/18/how-to-create-a-custom-django-middleware.html