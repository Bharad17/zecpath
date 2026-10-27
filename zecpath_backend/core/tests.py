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
