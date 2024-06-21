from django.core.management.base import BaseCommand
import pandas as pd
import os
import glob
import re


class Command(BaseCommand):
    help = 'Adds basic required data in database'

    @staticmethod
    def get_pod_image_name():
        directory_path = "C:\\Users\\akash\\OneDrive\\Desktop\\data\\5 Years POD April -June 24"
        image_files = glob.glob(os.path.join(directory_path, '*.*'))
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        image_files = [file for file in image_files if os.path.splitext(
            file)[1].lower() in image_extensions]
        image_filenames = [os.path.basename(file) for file in image_files]
        return image_filenames

    def handle(self, *args, **kwargs):
        file_path = "C:\\Users\\akash\\OneDrive\\Desktop\\data\\5 Years POD April -June 24\\sample.xls"

        # Read the specified sheet from the Excel file
        df = pd.read_excel(file_path, sheet_name='5 years')

        # Forward fill the 'POD NO.' column to handle merged cells
        df['POD NO.'] = df['POD NO.'].ffill()

        # Convert 'POD NO.' column to integers and then to strings to remove '.0'
        df['POD NO.'] = df['POD NO.'].apply(
            lambda x: str(int(float(x))) if pd.notnull(x) else '')

        # Get all POD image filenames
        all_pod_images = self.get_pod_image_name()

        # Function to extract numeric part from filename
        def extract_pod_number(filename):
            match = re.search(r'POD[\s_](\d+)', filename)
            if match:
                return match.group(1)
            else:
                return None

        # Create a mapping from POD number to image filename
        pod_image_map = {}
        for image_filename in all_pod_images:
            pod_number = extract_pod_number(image_filename)
            if pod_number:
                pod_image_map[pod_number] = image_filename

        # Add 'POD_image' column to df
        df['POD_image'] = df['POD NO.'].map(pod_image_map)

        # Print pod_image_map for debugging
        print("POD Image Map:")
        print(pod_image_map)

        # Print df for debugging
        print("DataFrame with POD Images:")
        print(df)

        # Save the updated DataFrame or perform further operations
        # For example:
        # df.to_excel('output_with_images.xlsx', index=False)
