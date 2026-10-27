
import os

from django.core.files.storage import default_storage
from django.db import transaction
from django.http import FileResponse

from rest_framework.parsers import FormParser, MultiPartParser

from .serializers import ResumeUploadSerializer, calculate_sha256
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import User, Candidate, Employer
from .serializers import (
    CandidateProfileSerializer,
    EmployerProfileSerializer,
)


from rest_framework.exceptions import PermissionDenied, ParseError, NotFound

def get_profile_target(request, expected_role):
    # Regular users can access only their own matching profile.
    if request.user.role != "ADMIN":
        if request.user.role != expected_role:
            raise PermissionDenied("Access denied. Role violation.")
        return request.user, None

    # Admins must specify the user whose profile they manage.
    user_id = request.query_params.get("user_id")

    if not user_id:
        raise ParseError("Admins must provide a user_id query parameter.")

    target = User.objects.filter(
        pk=user_id,
        role=expected_role,
    ).first()

    if not target:
        raise NotFound(f"{expected_role.title()} user not found.")

    return target, None


class CandidateProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user, error = get_profile_target(request, "CANDIDATE")
        if error:
            return error

        profile = Candidate.objects.filter(
            user=user, is_deleted=False
        ).first()

        if not profile:
            raise NotFound("Candidate profile not found.")

        return Response(CandidateProfileSerializer(profile).data)

    def post(self, request):
        user, error = get_profile_target(request, "CANDIDATE")
        if error:
            return error

        profile = Candidate.objects.filter(user=user).first()

        if profile and not profile.is_deleted:
            return Response(
                {"detail": "Candidate profile already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Restore a soft-deleted profile instead of violating OneToOne.
        serializer = CandidateProfileSerializer(
            instance=profile,
            data=request.data,
            partial=bool(profile),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, is_deleted=False)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK if profile else status.HTTP_201_CREATED,
        )

    def put(self, request):
        user, error = get_profile_target(request, "CANDIDATE")
        if error:
            return error

        profile = Candidate.objects.filter(
            user=user, is_deleted=False
        ).first()

        if not profile:
            return Response(
                {"detail": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CandidateProfileSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        user, error = get_profile_target(request, "CANDIDATE")
        if error:
            return error

        updated = Candidate.objects.filter(
            user=user, is_deleted=False
        ).update(is_deleted=True)

        if not updated:
            return Response(
                {"detail": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployerProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user, error = get_profile_target(request, "EMPLOYER")
        if error:
            return error

        profile = Employer.objects.filter(
            user=user, is_deleted=False
        ).first()

        if not profile:
            return Response(
                {"detail": "Employer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(EmployerProfileSerializer(profile).data)

    def post(self, request):
        user, error = get_profile_target(request, "EMPLOYER")
        if error:
            return error

        profile = Employer.objects.filter(user=user).first()

        if profile and not profile.is_deleted:
            return Response(
                {"detail": "Employer profile already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EmployerProfileSerializer(
            instance=profile,
            data=request.data,
            partial=bool(profile),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, is_deleted=False)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK if profile else status.HTTP_201_CREATED,
        )

    def put(self, request):
        user, error = get_profile_target(request, "EMPLOYER")
        if error:
            return error

        profile = Employer.objects.filter(
            user=user, is_deleted=False
        ).first()

        if not profile:
            return Response(
                {"detail": "Employer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployerProfileSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        user, error = get_profile_target(request, "EMPLOYER")
        if error:
            return error

        updated = Employer.objects.filter(
            user=user, is_deleted=False
        ).update(is_deleted=True)

        if not updated:
            return Response(
                {"detail": "Employer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
class CandidateResumeAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def _get_candidate_profile(self, request):
        user, error = get_profile_target(request, "CANDIDATE")

        if error:
            return None, error

        profile = Candidate.objects.filter(
            user=user,
            is_deleted=False,
        ).first()

        if not profile:
            return None, Response(
                {"detail": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return profile, None

    def _save_resume(self, request, profile, response_status):
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["resume"]
        file_size = uploaded_file.size
        file_hash = calculate_sha256(uploaded_file)

        # Avoid uploading the same resume again.
        if profile.resume and file_hash == profile.resume_sha256:
            return Response(
                {"detail": "This resume is already uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_name = profile.resume.name if profile.resume else None
        old_storage = profile.resume.storage if profile.resume else None

        profile.resume = uploaded_file
        profile.resume_sha256 = file_hash
        profile.save(update_fields=["resume", "resume_sha256"])

        # Delete the old file only after the database update commits.
        if old_name and old_name != profile.resume.name:
            transaction.on_commit(
                lambda name=old_name, storage=old_storage:
                    storage.delete(name)
            )

        return Response(
            {
                "detail": (
                    "Resume uploaded successfully."
                    if response_status == status.HTTP_201_CREATED
                    else "Resume replaced successfully."
                ),
                "has_resume": True,
                "file_size_bytes": file_size,
            },
            status=response_status,
        )

    def post(self, request):
        """Upload the first resume."""
        profile, error = self._get_candidate_profile(request)

        if error:
            return error

        if profile.resume:
            return Response(
                {"detail": "A resume already exists. Use PUT to replace it."},
                status=status.HTTP_409_CONFLICT,
            )

        return self._save_resume(
            request,
            profile,
            status.HTTP_201_CREATED,
        )

    def put(self, request):
        """Replace an existing resume."""
        profile, error = self._get_candidate_profile(request)

        if error:
            return error

        if not profile.resume:
            return Response(
                {"detail": "No resume exists. Use POST to upload it first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return self._save_resume(
            request,
            profile,
            status.HTTP_200_OK,
        )

    def get(self, request):
        """Download a resume only after authentication and authorization."""
        profile, error = self._get_candidate_profile(request)

        if error:
            return error

        if not profile.resume:
            return Response(
                {"detail": "No resume uploaded."},
                status=status.HTTP_404_NOT_FOUND,
            )

        stored_name = profile.resume.name
        storage = profile.resume.storage

        if not storage.exists(stored_name):
            return Response(
                {"detail": "Resume file not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        extension = os.path.splitext(stored_name)[1].lower()
        file_handle = profile.resume.open("rb")

        return FileResponse(
            file_handle,
            as_attachment=True,
            filename=f"resume{extension}",
        )

    def delete(self, request):
        """Delete the current resume without deleting the profile."""
        profile, error = self._get_candidate_profile(request)

        if error:
            return error

        if not profile.resume:
            return Response(
                {"detail": "No resume uploaded."},
                status=status.HTTP_404_NOT_FOUND,
            )

        old_name = profile.resume.name
        old_storage = profile.resume.storage

        profile.resume = None
        profile.resume_sha256 = ""
        profile.save(update_fields=["resume", "resume_sha256"])

        transaction.on_commit(
            lambda name=old_name, storage=old_storage:
                storage.delete(name)
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
