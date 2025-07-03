import os
from io import BytesIO
from rest_framework import status
from rest_framework.response import Response
import utils.s3 as s3_utils


def get_path_from_user_id(user_id, file_parameter_name, filename):
    return f"users/{user_id}/{file_parameter_name}/{filename}"


def upload_request_file(userid, file_parameter_name, file_bytes, filename, bucket):
    s3_path = get_path_from_user_id(userid, file_parameter_name, filename)
    if 'application_files' in file_parameter_name:
        s3_utils.upload_doc_stream(file_bytes, bucket, s3_path)
    else:
        s3_utils.upload_file_stream(file_bytes, bucket, s3_path)
    return s3_path


def upload_file_to_s3(request):
    file = request.FILES.get('file', None)
    file_upload_category = request.data.get('file_upload_category', 'application_files')
    if file and file_upload_category == "Org_Logo" and file.content_type != "image/svg+xml":
        return Response({'error': 'Only svg files are supported.'}, status=status.HTTP_400_BAD_REQUEST)
    bucket = os.getenv("PUBLIC_S3_BUCKET") if request.data.get('upload_type', 'private') == 'public' else os.getenv("S3_BUCKET")
    if file:
        user_id = request.user.id
        filename = file.name
        stream = file.file.read()
        file_bytes = BytesIO(stream)
        s3_url = upload_request_file(user_id, file_upload_category, file_bytes, filename, bucket)
        return Response({'s3_url': s3_url}, status=status.HTTP_200_OK)
    return Response({'error': "No file to upload"}, status=status.HTTP_400_BAD_REQUEST)
