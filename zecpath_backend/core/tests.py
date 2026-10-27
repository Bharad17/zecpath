from datetime import datetime, timezone

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Candidate, Employer, Job, User, application


class Day14ListAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employer_user = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            phone="10000000001",
            password="StrongPass123!",
            role="EMPLOYER",
        )
        self.employer = Employer.objects.get(user=self.employer_user)
        self.employer.company_name = "Example"
        self.employer.save(update_fields=["company_name"])
        self.candidate_user = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            phone="10000000002",
            password="StrongPass123!",
            role="CANDIDATE",
        )
        self.candidate = Candidate.objects.get(user=self.candidate_user)
        self.client.force_authenticate(user=self.candidate_user)

    def test_jobs_are_paginated_and_searchable(self):
        Job.objects.create(employer=self.employer, title="Python Engineer")
        Job.objects.create(employer=self.employer, title="Product Designer")

        response = self.client.get("/api/jobs/?search=python&page_size=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Python Engineer")

    def test_applications_are_filtered_and_use_related_objects(self):
        matching_job = Job.objects.create(
            employer=self.employer,
            title="Python Engineer",
        )
        other_job = Job.objects.create(
            employer=self.employer,
            title="Product Designer",
        )
        application.objects.create(
            user=self.candidate_user,
            candidate=self.candidate,
            job=matching_job,
            applied_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        )
        application.objects.create(
            user=self.candidate_user,
            candidate=self.candidate,
            job=other_job,
            applied_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        )

        with self.assertNumQueries(2):
            response = self.client.get(
                "/api/applications/?search=python&date_from=2026-10-01"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["job"], matching_job.id)


class Day15AuthenticationSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.candidate_user = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            phone="10000000011",
            password="Candidate-password-123!",
            role="CANDIDATE",
        )
        self.candidate = Candidate.objects.get(user=self.candidate_user)

    def test_public_signup_cannot_create_admin(self):
        response = self.client.post(
            "/api/signup/",
            {
                "username": "attacker",
                "email": "attacker@example.com",
                "phone": "10000000012",
                "password": "Attacker-password-123!",
                "role": "ADMIN",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="attacker@example.com").exists())

    def test_application_listing_is_scoped_to_candidate(self):
        employer_user = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            phone="10000000013",
            password="Employer-password-123!",
            role="EMPLOYER",
        )
        employer = Employer.objects.get(user=employer_user)
        first_job = Job.objects.create(employer=employer, title="First job")
        second_job = Job.objects.create(employer=employer, title="Second job")
        application.objects.create(
            user=self.candidate_user,
            candidate=self.candidate,
            job=first_job,
            applied_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        )
        other_user = User.objects.create_user(
            username="other_candidate",
            email="other@example.com",
            phone="10000000014",
            password="Other-password-123!",
            role="CANDIDATE",
        )
        application.objects.create(
            user=other_user,
            candidate=Candidate.objects.get(user=other_user),
            job=second_job,
            applied_at=datetime(2026, 10, 2, tzinfo=timezone.utc),
        )

        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get("/api/applications/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["job"], first_job.id)

    def test_login_and_protected_endpoint_require_valid_credentials(self):
        invalid_response = self.client.post(
            "/api/login/",
            {
                "email": "candidate@example.com",
                "password": "wrong-password",
            },
            format="json",
        )
        self.assertEqual(invalid_response.status_code, 401)

        missing_token_response = self.client.get("/api/user-test/")
        self.assertEqual(missing_token_response.status_code, 401)

        login_response = self.client.post(
            "/api/login/",
            {
                "email": "candidate@example.com",
                "password": "Candidate-password-123!",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data["data"])
        self.assertIn("refresh", login_response.data["data"])

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['data']['access']}"
        )
        protected_response = self.client.get("/api/user-test/")
        self.assertEqual(protected_response.status_code, 200)

    def test_logout_blacklists_refresh_token(self):
        login_response = self.client.post(
            "/api/login/",
            {
                "email": "candidate@example.com",
                "password": "Candidate-password-123!",
            },
            format="json",
        )
        refresh = login_response.data["data"]["refresh"]

        logout_response = self.client.post(
            "/api/logout/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(logout_response.status_code, 200)

        refresh_response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, 401)
