# authentication/views.py

from rest_framework.views import APIView

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer

from django.contrib.auth import authenticate
from .serializers import UserSerializer  
# def login_view(request):
#     user = authenticate(username=request.data['username'], password=request.data['password'])

#     if user is not None:
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'access_token': str(refresh.access_token),
#             'refresh_token': str(refresh),
#         }, status=status.HTTP_200_OK)
#     else:
#         return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response(
                    {'error': 'Please provide both email and password'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Print for debugging
            print(f"Attempting login for email: {email}")
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                })
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Exception as e:
            print(f"Login error: {str(e)}")  
            return Response(
                {'error': 'Login failed', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user