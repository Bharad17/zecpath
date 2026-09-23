from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Job
from .serializers import JobSerializer
class UserTestAPI(APIView):

    def get(self, request):
        return Response(
            {"message": "User API is working"},
            status=status.HTTP_200_OK
        )
class JobListAPI(APIView):
    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many = True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    def post(self, request):
        serializer = JobSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )




