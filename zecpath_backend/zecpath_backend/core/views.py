from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsEmployer
from django.utils import timezone
from .models import Candidate, application
from .serializers import ApplicationSerializer
from .permissions import IsCandidate
from .permissions import IsAdmin

from services.job_service import get_all_jobs,create_job
from .serializers import JobSerializer, SignupSerializer, LoginSerializer

class LoginAPI(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )
class LogoutAPI(APIView):

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserTestAPI(APIView):
    def get(self, request):
        return Response(
            {"message": "User API is working"},
            status=status.HTTP_200_OK
        )
    
class SignupAPI(APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "User created successfully",
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class JobListAPI(APIView):
    permission_classes = [IsEmployer]
    def get(self, request):
        jobs = get_all_jobs()
        serializer = JobSerializer(jobs, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            job = create_job(serializer.validated_data)
            response_serializer = JobSerializer(job)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ApplicationAPI(APIView):
    permission_classes = [IsCandidate]

    def post(self, request):
        try:
            candidate = Candidate.objects.get(user=request.user)
        except Candidate.DoesNotExist:
            return Response(
                {"error": "Candidate profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ApplicationSerializer(data=request.data)

        if serializer.is_valid():
            app = application.objects.create(
                job=serializer.validated_data['job'],
                candidate=candidate,
                user=request.user,
                applied_at=timezone.now()
            )

            response_serializer = ApplicationSerializer(app)

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class AdminControlAPI(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(
            {"message": "Admin control API is working"},
            status=status.HTTP_200_OK
        )




