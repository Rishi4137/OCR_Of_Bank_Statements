# s3_extraction.py
import random
import boto3
from PIL import Image
from io import BytesIO
import json

def fetch_documents_from_s3(bucket_name, folder_prefix, num_documents):
    """
    Fetches documents from the specified folder in an S3 bucket and returns them as a list of PIL images.
    
    Parameters:
    - bucket_name: Name of the S3 bucket.
    - folder_prefix: The folder prefix to search for images.
    - num_documents: The number of documents to fetch from the folder.
    
    Returns:
    - A list of PIL images.
    """
    # AWS credentials setup (ensure secure handling of credentials in production)
    with open("config.json", "r") as f:
        config = json.load(f)

    aws_access_key_id = config["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = config["AWS_SECRET_ACCESS_KEY"]
    region_name = 'eu-north-1'

    # Initialize an S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    # List objects in the specified folder in the S3 bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

    # Extract image keys from the folder
    image_keys = [
        obj['Key'] for obj in response.get('Contents', [])
        if obj['Key'].endswith(('.jpg', '.jpeg', '.png'))
    ]

    if not image_keys:
        raise ValueError(f"No images found in folder: {folder_prefix}")

    # Randomly select the specified number of images
    selected_keys = random.sample(image_keys, min(num_documents, len(image_keys)))

    # Initialize list to store PIL images
    uploaded_files = []

    # Download and store selected images
    for file_key in selected_keys:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        image_data = response['Body'].read()
        image = Image.open(BytesIO(image_data))

        # Convert image to RGB if necessary
        if image.mode in ['RGBA', 'P']:
            image = image.convert('RGB')

        # Store in uploaded_files
        uploaded_files.append(image)

    return uploaded_files
