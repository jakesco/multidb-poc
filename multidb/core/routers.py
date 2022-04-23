class TenantRouter:
    """
    Primary router for tenant data.
    """
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure core models only end up in tenant databases
        """
        if db == 'default':
            return app_label != 'core'
        return app_label == 'core'


