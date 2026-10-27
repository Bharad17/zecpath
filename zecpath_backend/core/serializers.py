import hashlib
import os
import zipfile

from rest_framework import serializers

from services.auth_service import authenticate_by_email, issue_token_pair

from .models import Candidate, Employer, Job, User, application


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "title"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "role", "is_verified"]


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[("CANDIDATE", "Candidate"), ("EMPLOYER", "Employer")],
        default="CANDIDATE",
    )

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate_by_email(data["email"], data["password"])
        return issue_token_pair(user)


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = application
        fields = ["id", "job", "candidate", "applied_at"]
        read_only_fields = ["candidate", "applied_at"]


MAX_RESUME_SIZE = 5 * 1024 * 1024
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
DOC_MAGIC_BYTES = bytes.fromhex("D0CF11E0A1B11AE1")


def validate_resume_file(uploaded_file):
    extension = os.path.splitext(uploaded_file.name)[1].lower()

    if extension not in ALLOWED_RESUME_EXTENSIONS:
        raise serializers.ValidationError(
            "Only PDF, DOC, and DOCX files are allowed."
        )

    if uploaded_file.size == 0:
        raise serializers.ValidationError("The file is empty.")

    if uploaded_file.size > MAX_RESUME_SIZE:
        raise serializers.ValidationError("Resume size cannot exceed 5 MB.")

    try:
        uploaded_file.seek(0)
        header = uploaded_file.read(8)
        uploaded_file.seek(0)

        if extension == ".pdf" and not header.startswith(b"%PDF-"):
            raise serializers.ValidationError(
                "The file does not appear to be a valid PDF."
            )

        if extension == ".doc" and header != DOC_MAGIC_BYTES:
            raise serializers.ValidationError(
                "The file does not appear to be a valid DOC file."
            )

        if extension == ".docx":
            try:
                with zipfile.ZipFile(uploaded_file) as archive:
                    contents = set(archive.namelist())
            except (zipfile.BadZipFile, OSError) as exc:
                raise serializers.ValidationError(
                    "The file does not appear to be a valid DOCX."
                ) from exc

            required_files = {"[Content_Types].xml", "word/document.xml"}
            if not required_files.issubset(contents):
                raise serializers.ValidationError(
                    "The DOCX document structure is invalid."
                )
            if "word/vbaProject.bin" in contents:
                raise serializers.ValidationError(
                    "Macro-enabled documents are not accepted."
                )
    finally:
        uploaded_file.seek(0)

    return uploaded_file


def calculate_sha256(uploaded_file):
    digest = hashlib.sha256()
    try:
        uploaded_file.seek(0)
        for chunk in uploaded_file.chunks():
            digest.update(chunk)
    finally:
        uploaded_file.seek(0)
    return digest.hexdigest()


class CandidateProfileSerializer(serializers.ModelSerializer):
    has_resume = serializers.SerializerMethodField()

    def get_has_resume(self, obj):
        return bool(obj.resume and obj.resume.name)

    def validate_expected_salary(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Expected salary cannot be negative."
            )
        return value

    def validate_skills(self, value):
        if len(value) > 200:
            raise serializers.ValidationError(
                "Skills cannot exceed 200 characters."
            )
        return value

    class Meta:
        model = Candidate
        fields = [
            "id",
            "skills",
            "education",
            "experience",
            "expected_salary",
            "has_resume",
        ]
        read_only_fields = ["id", "has_resume"]


class ResumeUploadSerializer(serializers.Serializer):
    resume = serializers.FileField(allow_empty_file=False)

    def validate_resume(self, value):
        return validate_resume_file(value)


class EmployerProfileSerializer(serializers.ModelSerializer):
    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Company name cannot be empty."
            )
        return value

    def validate_company_size(self, value):
        if value and not value.strip():
            raise serializers.ValidationError(
                "Company size cannot contain only spaces."
            )
        return value

    class Meta:
        model = Employer
        fields = [
            "id",
            "company_name",
            "domain",
            "company_size",
            "is_verified",
        ]
        read_only_fields = ["id", "is_verified"]
