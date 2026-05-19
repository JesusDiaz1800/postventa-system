"""
User serializers for API
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, RolePermission

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (read operations)
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.SerializerMethodField()
    accessible_pages = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'created_at', 'updated_at',
            'phone', 'department', 'digital_signature', 'accessible_pages',
            'sap_user', 'permissions_override', 'pages_override'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'created_at', 'updated_at',
            'is_staff', 'is_superuser'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_accessible_pages(self, obj):
        try:
            from .permissions import get_accessible_pages
            return get_accessible_pages(obj)
        except ImportError:
            return []
        except Exception as e:
            # Fallback for safety
            return []


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for managing role permissions
    """
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'role_display', 'permissions', 'accessible_pages', 'updated_at']
        read_only_fields = ['id', 'updated_at']
        
    def get_role_display(self, obj):
        # Helper to get display name from User.ROLE_CHOICES
        # We need to find the choice label for the stored role key
        for code, label in User.ROLE_CHOICES:
            if code == obj.role:
                return label
        return obj.role

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Convert digital_signature to relative URL to avoid mixed content errors
        # When frontend is HTTPS and backend is HTTP (localhost)
        if data.get('digital_signature'):
            # Remove the domain part, keep only the path starting from /documentos/
            url = data['digital_signature']
            if 'localhost' in url or '127.0.0.1' in url:
                # Extract just the path after the domain
                if '/documentos/' in url:
                    data['digital_signature'] = url.split('/documentos/', 1)[1]
                    data['digital_signature'] = f'/documentos/{data["digital_signature"]}'
        
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError('Username y password son requeridos')
        
        return attrs

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'phone', 'department', 'password', 'password_confirm',
            'sap_user', 'sap_password', 'permissions_override', 'pages_override'
        ]
    
    def validate(self, attrs):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"UserCreateSerializer.validate called with attrs: {attrs}")
        
        if attrs['password'] != attrs['password_confirm']:
            logger.error("Password confirmation mismatch")
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        logger.info("Password validation passed")
        return attrs
    
    def validate_username(self, value):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Validating username: {value}")
        
        if User.objects.filter(username=value).exists():
            logger.error(f"Username already exists: {value}")
            raise serializers.ValidationError("Este nombre de usuario ya existe")
        
        logger.info(f"Username validation passed: {value}")
        return value
    
    def validate_email(self, value):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Validating email: {value}")
        
        if User.objects.filter(email=value).exists():
            logger.error(f"Email already exists: {value}")
            raise serializers.ValidationError("Este email ya está registrado")
        
        logger.info(f"Email validation passed: {value}")
        return value

    def validate_permissions_override(self, value):
        if isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return value

    def validate_pages_override(self, value):
        if isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return value
    
    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"UserCreateSerializer.create called with data: {validated_data}")
        
        try:
            validated_data.pop('password_confirm')
            password = validated_data.pop('password')
            logger.info(f"Creating user with validated_data: {validated_data}")
            
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            
            logger.info(f"User created successfully: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating users
    """
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)
    digital_signature = serializers.ImageField(required=False, allow_null=True)
    sap_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'phone', 'department', 'password', 'password_confirm',
            'digital_signature', 'sap_user', 'sap_password',
            'permissions_override', 'pages_override'
        ]
    
    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
    def validate_digital_signature(self, value):
        """
        Validate digital_signature field.
        Handle cases where empty objects or invalid data is sent.
        """
        # If value is None or empty, that's valid (field is optional)
        if value is None or value == '':
            return None
        
        # If it's not a proper uploaded file, ignore it
        # This handles cases where FormData serialization fails
        if not hasattr(value, 'read'):
            return None
            
        return value
    
    def validate_username(self, value):
        # Check if username is being changed and if it already exists
        if self.instance and self.instance.username != value:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("Este nombre de usuario ya existe")
        return value
    
    def validate_email(self, value):
        # Check if email is being changed and if it already exists
        if self.instance and self.instance.email != value:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Este email ya está registrado")
        return value

    def validate_permissions_override(self, value):
        """Handle JSON strings from FormData"""
        if isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Formato JSON inválido para permisos")
        return value

    def validate_pages_override(self, value):
        """Handle JSON strings from FormData"""
        if isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Formato JSON inválido para páginas")
        return value
    
    def update(self, instance, validated_data):
        # Handle password update
        if 'password' in validated_data and validated_data['password']:
            password = validated_data.pop('password')
            instance.set_password(password)
        elif 'password' in validated_data:
            validated_data.pop('password')
            
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        
        # Protect sap_password from being wiped out if sent blank form data
        if 'sap_password' in validated_data and not validated_data['sap_password']:
            validated_data.pop('sap_password')
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for user lists
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'date_joined', 'last_login',
            'phone', 'department'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()