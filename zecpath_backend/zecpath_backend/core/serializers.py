from rest_framework import serializers
from .models import Job, User, application, Candidate, Employer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'is_verified']

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'password',
            'role',
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=validated_data['role'],
        )

        return user
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email']
        password = data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        user = authenticate(
            username=user.username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = application
        fields = ['id', 'job', 'candidate', 'applied_at']
        read_only_fields = ['candidate', 'applied_at']
class CandidateProfileSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["id"]


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