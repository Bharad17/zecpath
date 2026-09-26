from core.models import Job


def get_all_jobs():
    return Job.objects.all()

def create_job(data):
    return Job.objects.create(**data)
    