
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import User, Candidate, Employer
from .serializers import (
    CandidateProfileSerializer,
    EmployerProfileSerializer,
)


def get_profile_target(request, expected_role):
    # Regular users can access only their own matching profile.
    if request.user.role != "ADMIN":
        if request.user.role != expected_role:
            return None, Response(
                {"detail": "Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return request.user, None

    # Admins must specify the user whose profile they manage.
    user_id = request.query_params.get("user_id")

    if not user_id:
        return None, Response(
            {"detail": "Admins must provide a user_id query parameter."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    target = User.objects.filter(
        pk=user_id,
        role=expected_role,
    ).first()

    if not target:
        return None, Response(
            {"detail": f"{expected_role.title()} user not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

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
            return Response(
                {"detail": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

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
