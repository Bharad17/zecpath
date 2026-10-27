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
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Login successful",
                "data": serializer.validated_data,
            },
            status=status.HTTP_200_OK
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

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": "User created successfully",
                "data": {"user_id": user.id},
            },
            status=status.HTTP_201_CREATED
        )

class JobListAPI(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsEmployer()]
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]

    def get(self, request):
        jobs = get_all_jobs()
        serializer = JobSerializer(jobs, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = create_job(serializer.validated_data)
        response_serializer = JobSerializer(job)
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": "Job created successfully",
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

class ApplicationAPI(APIView):
    permission_classes = [IsCandidate]

    def post(self, request):
        candidate = Candidate.objects.filter(user=request.user, is_deleted=False).first()
        if not candidate:
            return Response(
                {"detail": "Candidate profile not found or inactive."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.validated_data['job']

        # Duplicate application prevention
        if application.objects.filter(candidate=candidate, job=job).exists():
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You have already applied for this job.",
                    "errors": {"job": ["Duplicate application not permitted."]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        app = application.objects.create(
            job=job,
            candidate=candidate,
            user=request.user,
            applied_at=timezone.now()
        )

        response_serializer = ApplicationSerializer(app)
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": "Job application submitted successfully",
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED
        )
class AdminControlAPI(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(
            {"message": "Admin control API is working"},
            status=status.HTTP_200_OK
        )






class Trigger500API(APIView):
    """Testing endpoint for Day 13 Status Code Standardization (500 Internal Server Error)."""
    def get(self, request):
        raise RuntimeError("Simulated unhandled internal server error for Day 13 testing.")
