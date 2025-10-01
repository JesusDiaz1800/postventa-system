"""
User serializers for API
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (read operations)
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'created_at', 'updated_at',
            'phone', 'department'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'created_at', 'updated_at',
            'is_staff', 'is_superuser'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def to_representation(self, instance):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"UserSerializer.to_representation called for user: {instance.username}")
        data = super().to_representation(instance)
        logger.info(f"Serialized user data: {data}")
        
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
            'is_active', 'phone', 'department', 'password', 'password_confirm'
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
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'phone', 'department', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
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
    
    def update(self, instance, validated_data):
        # Handle password update
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        
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