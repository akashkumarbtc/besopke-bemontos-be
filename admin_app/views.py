from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework.decorators import api_view
from .models import POD
from .serializers import PODSerializer
import pandas as pd
import os
import glob
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_excel_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        save_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_files')

        # Create the directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save the uploaded Excel file
        save_path = os.path.join(save_dir, excel_file.name)
        with open(save_path, 'wb+') as destination:
            for chunk in excel_file.chunks():
                destination.write(chunk)

        # Process the uploaded Excel file
        df = pd.read_excel(save_path, sheet_name='5 years')

        # Forward fill the 'POD NO.' column to handle merged cells
        df['POD NO.'] = df['POD NO.'].ffill()
        df['DESP.ON'] = df['DESP.ON'].ffill()

        # Convert 'POD NO.' column to integers and then to strings to remove '.0'
        df['POD NO.'] = df['POD NO.'].apply(
            lambda x: str(int(float(x))) if pd.notnull(x) else '')

        # Get all POD image filenames
        directory_path = "C:\\Users\\akash\\OneDrive\\Desktop\\data\\5 Years POD April -June 24"
        image_files = glob.glob(os.path.join(directory_path, '*.*'))
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        image_files = [file for file in image_files if os.path.splitext(
            file)[1].lower() in image_extensions]
        image_filenames = [os.path.basename(file) for file in image_files]

        # Function to extract numeric part from filename
        def extract_pod_number(filename):
            match = re.search(r'POD[\s_](\d+)', filename)
            if match:
                return match.group(1)
            else:
                return None

        # Create a mapping from POD number to image filename
        pod_image_map = {}
        for image_filename in image_filenames:
            pod_number = extract_pod_number(image_filename)
            if pod_number:
                pod_image_map[pod_number] = image_filename

        # Save POD numbers and image filenames to database
        for index, row in df.iterrows():
            pod_number = row['POD NO.']
            pod_image_filename = pod_image_map.get(pod_number, None)

            desp_on_value = pd.to_datetime(row['DESP.ON']).date(
            ) if pd.notnull(row['DESP.ON']) else None
            received_date_value = pd.to_datetime(row['Received Date']).date(
            ) if pd.notnull(row['Received Date']) else None

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
                pod_image=pod_image_filename
            )

        # Serialize data for response
        pods = POD.objects.all()
        serializer = PODSerializer(pods, many=True)

        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({'error': 'File upload failed.'})
