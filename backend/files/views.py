from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import File
from .serializers import FileSerializer
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.client import Config
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import boto3
import uuid
import time
import os
import logging
# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getFilesList(request):
    user = request.user
    notes = File.objects.filter(user=user).order_by('-updated_at')
    serializer = FileSerializer(notes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getFile(request, pk):
    note = File.objects.get(id=pk)
    serializer = FileSerializer(note, many=False)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPresignedUrl(request, pk):
    file = File.objects.get(id=pk)
    presigned_url = generate_presigned_url(file.s3_key)
    if not presigned_url:
        return Response({"error": "Failed to generate presigned URL."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"url": presigned_url})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createFile(request):
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    unique_filename = generate_unique_filename(request.user.id, uploaded_file.name)

    try:
        # Attempt to upload the file to S3
        s3.upload_fileobj(
            uploaded_file,
            settings.AWS_STORAGE_BUCKET_NAME,  # Assume this is set in your Django settings or environment
            unique_filename,
            ExtraArgs={
                "ContentType": uploaded_file.content_type
            }
        )
    except ClientError as e:
        # Handle AWS S3 client exceptions
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # If upload succeeds, create the File record
    s3_key = unique_filename

    file = File.objects.create(name=uploaded_file.name, s3_key=s3_key, user=request.user)
    
    serializer = FileSerializer(file, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
# def createFile(request):
#     uploaded_file = request.FILES['file']
#     if not uploaded_file:
#         return Response({'message': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
#     s3 = boto3.client('s3')
#     # Generate a unique file name
#     unique_filename = generate_unique_filename(uploaded_file)
    
#     try:
#         # Check if file exists, otherwise proceed with upload
#         s3.head_object(Bucket='simplenotes', Key=unique_filename)
#     except:  # If file does not exist, proceed with upload
#         s3_response = s3.upload_fileobj(
#             uploaded_file,
#             'simplenotes',
#             unique_filename,
#             ExtraArgs={
#                 "ACL": "public-read",
#                 "ContentType": uploaded_file.content_type
#             }
#         )
#         s3_url = f"https://simplenotes.s3.amazonaws.com/{unique_filename}"
#         file = File.objects.create(name=uploaded_file.name, s3_url=s3_url, user=request.user)
#         serializer = FileSerializer(file, many=False)
#         return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateFile(request, pk):
    data = request.data
    file = File.objects.get(id=pk)
    serializer = FileSerializer(instance=file, data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteFile(request, pk):
    file = File.objects.get(id=pk)
    file.delete()
    return Response({'message': 'File deleted', 'id': pk})

def generate_unique_filename(user_id, filename):
    # timestamp = str(int(time.time()))
    # unique_id = str(uuid.uuid4())[:8]  # Generate a unique ID
    # filename, file_extension = os.path.splitext(file.name)
    # return f"{filename}_{timestamp}_{unique_id}{file_extension}"
    return f"uploads/{user_id}/{filename}"

def generate_presigned_url(s3_key, expiration=3600):
    """
    Generate a presigned URL to share an S3 object
    :param s3_key: the object key in S3 bucket
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=settings.AWS_S3_REGION_NAME,
                             config=Config(signature_version='s3v4'),
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                            'Key': s3_key},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response