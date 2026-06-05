import secrets
from datetime import timedelta
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.models import User, PendingRegistration
from user.permissions import UserPermission
from user.serializers import UserSerializer, RegisterSerializer


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == "admin":
            return User.objects.all()
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def start_signup(self, request):
        """Validate signup data, store pending registration, send verification email."""
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        email = data['email']
        # Reject if user already exists
        if User.objects.filter(username=data['username']).exists():
            return Response({'username': ['A user with that username already exists.']}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'email': ['A user with that email already exists.']}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(phone_number=data['phone_number']).exists():
            return Response({'phone_number': ['A user with that phone number already exists.']}, status=status.HTTP_400_BAD_REQUEST)
        # Invalidate any existing pending for this email
        PendingRegistration.objects.filter(email=email).delete()
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        pref = data.get('preferred_contact_method') or None
        PendingRegistration.objects.create(
            email=email,
            token=token,
            username=data['username'],
            password=make_password(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone_number=data['phone_number'],
            preferred_contact_method=pref,
            expires_at=expires_at,
        )
        verify_url = f"{getattr(settings, 'FRONTEND_VERIFY_EMAIL_URL', 'http://localhost:3000/verify-email')}?token={token}"
        send_mail(
            subject='Verify your Flight Buddy account',
            message=f'Click the link below to verify your email and create your account:\n\n{verify_url}\n\nThis link expires in 24 hours.',
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'detail': 'Verification email sent. Check your inbox.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET', 'POST'], permission_classes=[AllowAny])
    def verify_email(self, request):
        """Verify token and create user. Token in body: { \"token\": \"...\" } or query: ?token=..."""
        data = getattr(request, 'data', None) or {}
        params = getattr(request, 'query_params', None) or {}
        token = (
            data.get('token') or data.get('verification_token') or data.get('email_token')
            or params.get('token') or params.get('verification_token') or params.get('email_token')
            or ''
        )
        if isinstance(token, list):
            token = token[0] if token else ''
        token = str(token).strip()
        if not token:
            return Response(
                {'detail': 'Token is required.', 'code': 'token_missing'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token_decoded = unquote(token)
        try:
            pending = PendingRegistration.objects.get(token=token_decoded)
        except PendingRegistration.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired link. If you already verified, try signing in.', 'code': 'invalid_token'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if timezone.now() > pending.expires_at:
            pending.delete()
            return Response(
                {'detail': 'Verification link has expired.', 'code': 'link_expired'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=pending.username).exists() or User.objects.filter(email=pending.email).exists():
            pending.delete()
            return Response(
                {'detail': 'Account already exists. You can sign in.', 'code': 'account_exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pref = pending.preferred_contact_method or None
        try:
            user = User(
                username=pending.username,
                email=pending.email,
                first_name=pending.first_name or '',
                last_name=pending.last_name or '',
                phone_number=pending.phone_number,
                preferred_contact_method=pref,
                role='user',
            )
            user.password = pending.password  # already hashed; assign directly to avoid double-hashing
            user.save()
        except Exception as e:
            return Response(
                {'detail': f'Could not create account: {str(e)}', 'code': 'create_failed'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pending.delete()
        return Response({'detail': 'Account created. You can sign in now.'}, status=status.HTTP_201_CREATED)


class UserTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]


class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]