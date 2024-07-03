import os
import re
import glob
import zipfile
import base64
import pandas as pd
from .models import POD
from django.conf import settings
from rest_framework import status
from django.db import transaction
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from .serializers import PODSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PODPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100


class PODViewSet(ModelViewSet):
    queryset = POD.objects.all()
    serializer_class = PODSerializer
    pagination_class = PODPagination


def save_uploaded_file(file, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, file.name)
    try:
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    except Exception as e:
        raise Exception(f'Failed to save file: {str(e)}')
    return save_path


def extract_zip_file(zip_path, extract_dir):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        raise Exception(f'Failed to extract ZIP file: {str(e)}')
    return extract_dir


def create_pod_image_map(image_files):
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    image_files = [file for file in image_files if os.path.splitext(
        file)[1].lower() in image_extensions]
    image_filenames = [os.path.basename(file) for file in image_files]

    def extract_pod_number(filename):
        match = re.search(r'POD[\s_](\d+)', filename)
        if match:
            return match.group(1)
        else:
            return None

    pod_image_map = {}
    for image_filename in image_filenames:
        pod_number = extract_pod_number(image_filename)
        if pod_number:
            pod_image_map[pod_number] = image_filename
    return pod_image_map


def save_pod_data(df, pod_image_map, base_dir):
    with transaction.atomic():
        for index, row in df.iterrows():
            pod_number = row['POD NO.']
            pod_image_filename = pod_image_map.get(pod_number, None)

            desp_on_value = pd.to_datetime(row['DESP.ON']).date(
            ) if pd.notnull(row['DESP.ON']) else None
            received_date_value = pd.to_datetime(row['Received Date']).date(
            ) if pd.notnull(row['Received Date']) else None

            if pod_image_filename:
                pod_image_path = os.path.join(base_dir, pod_image_filename)
                with open(pod_image_path, 'rb') as f:
                    pod_image_data = f.read()
            else:
                pod_image_data = None

            POD.objects.create(
                sr_no=row['Sr.No'],
                employee_code=row['EMPLOYEE CODE'],
                employee_name=row['EMPLOYEE NAME'],
                to_be_sent_to_e_name=row['To be sent to E name'],
                secretary_code=row['Secretary code'],
                address=row['Address'],
                mobile_no=row['Mobile no'],
                pod_number=pod_number,
                desp_on=desp_on_value,
                received_date=received_date_value,
                pod_image=pod_image_data
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_zip_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        zip_file = request.FILES['file']

        if not zip_file.name.endswith('.zip'):
            return JsonResponse({'error': 'Invalid file format. Please upload a ZIP file.'}, status=400)

        save_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_files')

        try:
            zip_path = save_uploaded_file(zip_file, save_dir)
            extracted_files_dir = extract_zip_file(
                zip_path, os.path.splitext(zip_path)[0])
            xls_files = glob.glob(os.path.join(
                extracted_files_dir, '**', '*.xls'), recursive=True)
            image_files = glob.glob(os.path.join(
                extracted_files_dir, '**', '*.*'), recursive=True)

            if not xls_files:
                return JsonResponse({'error': 'No .xls files found in the ZIP archive.'}, status=400)

            # Assuming all image files are found within the extracted directory
            base_dir = os.path.commonpath(image_files)
            pod_image_map = create_pod_image_map(image_files)
            process_excel_files(xls_files, pod_image_map, base_dir)

            pods = POD.objects.all()
            serializer = PODSerializer(pods, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'File upload failed.'}, status=400)


def process_excel_files(xls_files, pod_image_map, base_dir):
    for xls_file in xls_files:
        df = pd.read_excel(xls_file, sheet_name='5 years')
        df['POD NO.'] = df['POD NO.'].ffill()
        df['DESP.ON'] = df['DESP.ON'].ffill()
        df['POD NO.'] = df['POD NO.'].apply(
            lambda x: str(int(float(x))) if pd.notnull(x) else '')
        save_pod_data(df, pod_image_map, base_dir)
