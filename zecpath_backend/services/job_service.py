from core.models import Job


def get_all_jobs(*, search=None, role=None):
    queryset = Job.objects.select_related("employer__user").all()

    if search:
        queryset = queryset.filter(title__icontains=search)
    if role:
        queryset = queryset.filter(employer__user__role=role)

    return queryset.order_by("id")

def create_job(data):
    return Job.objects.create(**data)
    