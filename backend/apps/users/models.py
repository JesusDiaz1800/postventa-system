from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario es requerido')
        if not email:
            raise ValueError('El email es requerido')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('management', 'Gerencia'),
        ('technical_service', 'Servicio Técnico'),
        ('quality', 'Calidad'),
        ('supervisor', 'Supervisor Postventa'),
        ('analyst', 'Analista Técnico'),
        ('customer_service', 'Atención al Cliente'),
        ('provider', 'Proveedor'),
    ]
    
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Nombre de usuario único'
    )
    
    email = models.EmailField(
        unique=True,
        help_text='Email del usuario',
        db_index=True
    )
    
    first_name = models.CharField(
        max_length=150,
        blank=True,
        help_text='Nombre del usuario'
    )
    
    last_name = models.CharField(
        max_length=150,
        blank=True,
        help_text='Apellido del usuario'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='analyst',
        help_text='Rol del usuario en el sistema',
        db_index=True
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el usuario está activo'
    )
    
    is_staff = models.BooleanField(
        default=False,
        help_text='Indica si el usuario puede acceder al admin'
    )
    
    is_superuser = models.BooleanField(
        default=False,
        help_text='Indica si el usuario es superusuario'
    )
    
    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha de registro'
    )
    
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Último inicio de sesión'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación del usuario'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de última actualización'
    )
    
    # Additional fields for user profile
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Teléfono de contacto'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text='Departamento o área de trabajo'
    )
    
    digital_signature = models.ImageField(
        upload_to='users/signatures/',
        null=True,
        blank=True,
        verbose_name="Firma Digital",
        help_text="Imagen de la firma digital del usuario"
    )
    
    # Custom manager
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        # Disable Django's default groups and permissions
        default_permissions = ()
        permissions = []
    
    # Override the many-to-many fields to disable them
    # groups = None
    # user_permissions = None
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_supervisor(self):
        """Check if user is supervisor"""
        return self.role in ['admin', 'supervisor']
    
    def can_manage_incidents(self):
        """Check if user can manage incidents"""
        return self.role in ['admin', 'management', 'technical_service', 'quality']
    
    def can_view_reports(self):
        """Check if user can view reports"""
        return self.role in ['admin', 'management', 'technical_service', 'quality']
    
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['admin']
    
    def can_access_ai_analysis(self):
        """Check if user can access AI and analysis"""
        return self.role in ['admin', 'management', 'technical_service', 'quality']
    
    def can_access_workflows(self):
        """Check if user can access workflows"""
        return self.role in ['admin', 'management', 'technical_service', 'quality']
    
    def can_access_configuration(self):
        """Check if user can access configuration"""
        return self.role in ['admin', 'management', 'technical_service', 'quality']
    
    def can_access_documents(self):
        """Check if user can access documents"""
        return self.role in ['admin', 'management', 'quality']
    
    def can_access_quality_reports(self):
        """Check if user can access quality reports"""
        return self.role in ['admin', 'quality']
    
    # Override Django's default group and permission methods
    def get_group_permissions(self, obj=None):
        """Override to return empty permissions"""
        return set()
    
    def get_all_permissions(self, obj=None):
        """Override to return empty permissions"""
        return set()
    
    def has_perm(self, perm, obj=None):
        """Override to use role-based permissions"""
        from .permissions import has_permission
        return has_permission(self, perm)
    
    def has_perms(self, perm_list, obj=None):
        """Override to use role-based permissions"""
        from .permissions import has_permission
        return all(has_permission(self, perm) for perm in perm_list)
    
    def has_module_perms(self, app_label):
        """Override to use role-based permissions"""
        # Implement module-based permissions if needed
        return False
    
    def get_permissions(self):
        """Get all permissions for this user based on role"""
        from .permissions import get_user_permissions
        return get_user_permissions(self)
    
    def get_accessible_pages(self):
        """Get list of pages this user can access"""
        from .permissions import get_accessible_pages
        return get_accessible_pages(self)
    # ADVERTENCIA: Revisa los tipos de datos y relaciones para compatibilidad total con SQL Server. Evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
