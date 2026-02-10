"""
User management views for admin functionality
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, LoginSerializer
from .permissions import get_user_permissions, get_accessible_pages, RoleBasedPermission
import logging

logger = logging.getLogger(__name__)

class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Custom permission to only allow admins and supervisors to manage users
    """
    def has_permission(self, request, view):
        try:
            if not request.user or not request.user.is_authenticated:
                return False
            
            # Verificar si el usuario tiene permisos para gestionar usuarios
            from .permissions import has_permission
            return has_permission(request.user, 'can_manage_users')
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create a new user
    """
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    required_roles = ['admin', 'administrador', 'supervisor']
    
    def get_queryset(self):
        logger.info(f"UserListCreateView.get_queryset called by user: {self.request.user.username}")
        
        queryset = User.objects.all().order_by('-created_at')
        logger.info(f"Base queryset count: {queryset.count()}")
        
        # Filter by search term
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
            logger.info(f"After search filter '{search}': {queryset.count()}")
        
        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
            logger.info(f"After role filter '{role}': {queryset.count()}")
        
        # Filter by status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            logger.info(f"After status filter '{is_active}': {queryset.count()}")
        
        logger.info(f"Final queryset count: {queryset.count()}")
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def list(self, request, *args, **kwargs):
        logger.info(f"UserListCreateView.list called by user: {request.user.username}")
        logger.info(f"Request query params: {request.query_params}")
        
        queryset = self.filter_queryset(self.get_queryset())
        logger.info(f"Filtered queryset count: {queryset.count()}")
        
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"Serialized users count: {len(serializer.data)}")
        
        response = super().list(request, *args, **kwargs)
        logger.info(f"Response data type: {type(response.data)}")
        logger.info(f"Response data keys: {response.data.keys() if hasattr(response.data, 'keys') else 'No keys'}")
        
        return response
    
    def create(self, request, *args, **kwargs):
        logger.info(f"UserListCreateView.create called by user: {request.user.username}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request content type: {request.content_type}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            logger.info(f"Serializer data: {serializer.initial_data}")
            
            if serializer.is_valid():
                logger.info("Serializer is valid")
                user = serializer.save()
                logger.info(f"User created successfully: {user.username}")
                return Response(
                    UserSerializer(user).data, 
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in create method: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': str(e),
                'detail': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get user details with error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving user: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response(
                {'error': f'Error al obtener usuario: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        logger.info(f"UserRetrieveUpdateDestroyView.update called by user: {request.user.username}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request method: {request.method}")
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        logger.info(f"Updating user: {instance.username} (ID: {instance.id})")
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        logger.info(f"Serializer initial data: {serializer.initial_data}")
        
        if serializer.is_valid():
            logger.info("Serializer is valid")
            
            user = serializer.save()
            logger.info(f"User updated successfully: {user.username}")
            return Response(UserSerializer(user).data)
        else:
            logger.error(f"Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        logger.info(f"UserRetrieveUpdateDestroyView.destroy called by user: {request.user.username}")
        
        try:
            instance = self.get_object()
            logger.info(f"Attempting to delete user: {instance.username} (ID: {instance.id})")
        except Exception as e:
            logger.error(f"User not found: {e}")
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )        
        # Prevent admin from deleting themselves
        if instance == request.user:
            logger.warning(f"User {request.user.username} attempted to delete themselves")
            return Response(
                {'error': 'No puedes eliminar tu propia cuenta'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deleting the last admin
        if instance.role == 'admin':
            admin_count = User.objects.filter(role='admin', is_active=True).count()
            logger.info(f"Admin count: {admin_count}")
            if admin_count <= 1:
                logger.warning(f"Attempted to delete last admin: {instance.username}")
                return Response(
                    {'error': 'No se puede eliminar el último administrador'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        logger.info(f"Deleting user: {instance.username}")
        try:
            self.perform_destroy(instance)
            logger.info(f"User {instance.username} deleted successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting user {instance.username}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response(
                {'error': f'Error al eliminar usuario: {str(e)}. El usuario puede tener registros asociados.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrSupervisor])
def user_stats(request):
    """
    Get user statistics for dashboard
    """
    logger.info(f"user_stats called by user: {request.user.username}")
    logger.info(f"User role: {request.user.role}")
    logger.info(f"User is_active: {request.user.is_active}")
    
    try:
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_count = User.objects.filter(role='admin', is_active=True).count()
        supervisor_count = User.objects.filter(role='supervisor', is_active=True).count()
        analyst_count = User.objects.filter(role='analyst', is_active=True).count()
        customer_service_count = User.objects.filter(role='customer_service', is_active=True).count()
        
        # Recent users (last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_users = User.objects.filter(created_at__gte=thirty_days_ago).count()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'admin_count': admin_count,
            'supervisor_count': supervisor_count,
            'analyst_count': analyst_count,
            'customer_service_count': customer_service_count,
            'recent_users': recent_users,
        }
        
        logger.info(f"User stats calculated: {stats}")
        logger.info(f"Total users in database: {User.objects.count()}")
        logger.info(f"All users: {list(User.objects.values('username', 'role', 'is_active'))}")
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response(
            {'error': 'Error al obtener estadísticas de usuarios'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSupervisor])
def toggle_user_status(request, user_id):
    """
    Toggle user active status
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent admin from deactivating themselves
        if user == request.user:
            return Response(
                {'error': 'No puedes desactivar tu propia cuenta'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deactivating the last admin
        if user.role == 'admin' and user.is_active:
            admin_count = User.objects.filter(role='admin', is_active=True).count()
            if admin_count <= 1:
                return Response(
                    {'error': 'No se puede desactivar el último administrador'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'Usuario {"activado" if user.is_active else "desactivado"} exitosamente',
            'is_active': user.is_active
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error toggling user status: {e}")
        return Response(
            {'error': 'Error al cambiar el estado del usuario'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSupervisor])
def reset_user_password(request, user_id):
    """
    Reset user password to default
    """
    try:
        user = User.objects.get(id=user_id)
        default_password = 'Polifusion2024!'
        
        user.set_password(default_password)
        user.save()
        
        return Response({
            'message': 'Contraseña restablecida exitosamente',
            'new_password': default_password
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error resetting user password: {e}")
        return Response(
            {'error': 'Error al restablecer la contraseña'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint (Instrumented for Debugging)
    """
    logger.info("--- LOGIN ATTEMPT STARTED ---")
    try:
        # Log basic request info (sanitize password)
        data_safe = request.data.copy()
        if 'password' in data_safe:
            data_safe['password'] = '******'
            
        logger.info(f"Login request received from IP: {request.META.get('REMOTE_ADDR')}")
        logger.info(f"Login payload: {data_safe}")
        
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            logger.info("Serializer validation passed. Proceeding to authentication.")
            
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # Intentar autenticación con username primero
            logger.debug(f"Authenticating with username: {username}")
            user = authenticate(request, username=username, password=password)
            
            # Si no funciona, intentar con email
            if user is None:
                logger.debug("Username auth failed. Trying email lookup.")
                try:
                    user_obj = User.objects.get(email=username)
                    logger.debug(f"Found user by email: {user_obj.username}")
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    logger.debug("Email lookup failed or user does not exist.")
                    pass
            
            if user is not None:
                logger.info(f"Authentication successful for user: {user.username} (ID: {user.id})")
                
                if user.is_active:
                    # Update last_login explicitly
                    try:
                        from django.utils import timezone
                        logger.info("Updating last_login...")
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                        logger.info("last_login updated successfully.")
                    except Exception as eSave:
                        logger.error(f"Error updating last_login (non-fatal): {eSave}", exc_info=True)

                    # Generate JWT tokens
                    try:
                        logger.info("Generating JWT tokens...")
                        refresh = RefreshToken.for_user(user)
                        access_token = str(refresh.access_token)
                        refresh_token = str(refresh)
                        logger.info("Tokens generated successfully.")
                    except Exception as eToken:
                        logger.error(f"Error generating tokens: {eToken}", exc_info=True)
                        raise eToken

                    # Audit login
                    try:
                        from apps.audit.models import AuditLogManager
                        logger.info(f"Attempting to audit login for {user.username}")
                        AuditLogManager.log_action(
                            user=user,
                            action='user_login',
                            description=f'Usuario {user.username} inició sesión',
                            ip_address=request.META.get('REMOTE_ADDR'),
                            details={'user_agent': request.META.get('HTTP_USER_AGENT', '')}
                        )
                        logger.info("Audit login successful")
                    except Exception as eAudit:
                        logger.error(f"Failed to audit login (external): {eAudit}", exc_info=True)
                        # No lanzamos excepción aquí para no bloquear el login si falla el log

                    logger.info("Login flow completed successfully. Returning response.")
                    return Response({
                        'success': True,
                        'message': 'Inicio de sesión exitoso',
                        'access': access_token,
                        'refresh': refresh_token,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'role': user.role,
                            'is_active': user.is_active
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    logger.warning(f"User {user.username} found but is inactive.")
                    return Response({
                        'success': False,
                        'error': 'Usuario inactivo'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.warning(f"Authentication failed for: {username}")
                return Response({
                    'success': False,
                    'error': 'Credenciales inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            logger.warning(f"Serializer validation failed: {serializer.errors}")
            return Response({
                'success': False,
                'error': 'Datos inválidos',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.critical(f"FATAL LOGIN ERROR: {str(e)}", exc_info=True)
        # Check for IntegrityError specifically in the exception tree
        if 'IntegrityError' in str(type(e)) or 'IntegrityError' in str(e):
             logger.critical("INTEGRITY ERROR CONFIRMED DURING LOGIN EXECUTION")
        
        return Response({
            'success': False,
            'error': 'Error interno del servidor (Check logs)'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint - Blacklist the refresh token
    """
    try:
        # Para JWT, necesitamos blacklistear el refresh token
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as token_error:
                logger.warning(f"Token blacklist error: {token_error}")
                # No es crítico si no podemos blacklistear el token
        
        # Registrar en auditoría
        from apps.audit.models import AuditLogManager
        AuditLogManager.log_action(
            user=request.user,
            action='user_logout',  # Matched with signals
            description=f'Usuario {request.user.username} cerró sesión',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={
                'user_id': request.user.id,
                'username': request.user.username,
                'logout_method': 'jwt_blacklist'
            }
        )
        
        return Response({
            'success': True,
            'message': 'Cierre de sesión exitoso'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return Response({
            'success': False,
            'error': 'Error al cerrar sesión'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get or update current user profile
    """
    if request.method == 'PATCH':
        try:
            user = request.user
            # Use serializer to validate and save
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Return updated profile structure matches GET
                return Response({
                    'success': True,
                    'message': 'Perfil actualizado correctamente',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                        'is_active': user.is_active,
                        'phone': user.phone,
                        'department': user.department,
                        'digital_signature': request.build_absolute_uri(user.digital_signature.url) if user.digital_signature else None,
                        'last_login': user.last_login,
                        'created_at': user.created_at
                    }
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Datos inválidos',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return Response({
                'success': False,
                'error': 'Error al actualizar perfil'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # GET request
    try:
        user = request.user
        signature_url = None
        if user.digital_signature:
            try:
                signature_url = request.build_absolute_uri(user.digital_signature.url)
            except:
                pass

        return Response({
            'success': True,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return Response({
            'success': False,
            'error': 'Error al obtener perfil'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_auth(request):
    """
    Debug endpoint to check authentication
    """
    return Response({
        'user': request.user.username,
        'user_id': request.user.id,
        'user_role': request.user.role,
        'is_authenticated': request.user.is_authenticated,
        'can_manage_users': request.user.can_manage_users(),
        'auth_header': request.META.get('HTTP_AUTHORIZATION', 'No auth header'),
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_create_user(request):
    """
    Debug endpoint to test user creation with minimal data
    """
    logger.info(f"Debug create user called by: {request.user.username}")
    logger.info(f"Request data: {request.data}")
    logger.info(f"Request content type: {request.content_type}")
    
    try:
        # Test with minimal data
        test_data = {
            'username': 'testuser123',
            'email': 'test123@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'analyst',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'is_active': True
        }
        
        serializer = UserCreateSerializer(data=test_data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"Test user created successfully: {user.username}")
            return Response({
                'success': True,
                'message': 'Test user created successfully',
                'user': UserSerializer(user).data
            })
        else:
            logger.error(f"Test user validation failed: {serializer.errors}")
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in debug create user: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    """Get current user's permissions and accessible pages"""
    try:
        user = request.user
        
        permissions = get_user_permissions(user)
        accessible_pages = get_accessible_pages(user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'role_display': user.get_role_display(),
                'is_active': user.is_active,
            },
            'permissions': permissions,
            'accessible_pages': accessible_pages,
        })
        
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        return Response(
            {'error': 'Error al obtener permisos del usuario'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_own_password(request):
    """Allow users to change their own password"""
    try:
        user = request.user
        data = request.data
        
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')
        
        # Validar datos (excepto para admin principal)
        if user.username != 'jdiaz' and not current_password:
            return Response({'error': 'La contraseña actual es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({'error': 'La nueva contraseña es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({'error': 'La nueva contraseña debe tener al menos 6 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'error': 'Las contraseñas no coinciden'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar contraseña actual (excepto para admin principal)
        if user.username != 'jdiaz' and not user.check_password(current_password):
            return Response({'error': 'La contraseña actual es incorrecta'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        logger.info(f"User {user.username} changed their password")
        
        return Response({'message': 'Contraseña cambiada exitosamente'})
        
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return Response(
            {'error': 'Error al cambiar la contraseña'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, RoleBasedPermission])
def reset_user_password(request, user_id):
    """Allow admins/supervisors to reset user passwords"""
    try:
        # Verificar permisos
        from .permissions import has_permission
        if not has_permission(request.user, 'can_manage_users'):
            return Response({'error': 'No tienes permisos para restablecer contraseñas'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')
        
        # Validar datos
        if not new_password:
            return Response({'error': 'La nueva contraseña es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({'error': 'La nueva contraseña debe tener al menos 6 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'error': 'Las contraseñas no coinciden'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cambiar contraseña
        target_user.set_password(new_password)
        target_user.save()
        
        logger.info(f"User {request.user.username} reset password for user {target_user.username}")
        
        return Response({'message': f'Contraseña restablecida para {target_user.full_name}'})
        
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return Response(
            {'error': 'Error al restablecer la contraseña'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )