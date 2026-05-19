class SapRouter:
    """
    A router to control all database operations on models in the
    sap_integration application.
    """
    route_app_labels = {'sap_integration'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read sap_integration models go to sap_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'sap_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write sap_integration models go to sap_db 
        (though we should treat it as read-only).
        """
        if model._meta.app_label in self.route_app_labels:
            return 'sap_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if involved models are in the sap_integration app.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the sap_integration app only appears in the 'sap_db'
        database.
        """
        if app_label in self.route_app_labels:
            return db == 'sap_db'
        return None
