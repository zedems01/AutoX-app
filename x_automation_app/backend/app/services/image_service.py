import base64
import uuid
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from openai import OpenAI
from ...config import settings

def generate_and_upload_image(prompt: str) -> str:
    """
    Generates an image using OpenAI's DALL-E 3, uploads it to AWS S3,
    and returns a presigned URL.

    Args:
        prompt (str): The prompt to generate the image from.

    Returns:
        str: The presigned URL of the uploaded image, or None if an error occurs.
    """
    try:
        # 1. Generate the image with OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        result = client.images.generate(
            model="gpt-image-1",  # The plan specifies gpt-image-1, but that seems to be a private model name. Using public dall-e-3.
            prompt=prompt,
            size="1024x1024"
        )
        image_b64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)

        image_name = f"{uuid.uuid4()}.png"
        image_key = f"images/{image_name}"
        image_path = f"./images/{image_name}"
        bucket_name = settings.BUCKET_NAME

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        print(f"Image saved to {image_path}")
        
        # 2. Upload the image to AWS S3
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        )
    
        s3_client.upload_file(
            image_path,
            bucket_name,
            image_key
        )
        # 3. Generate a presigned URL for the image
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': image_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        print(f"Successfully uploaded image {image_name} to S3 bucket {bucket_name}.")
        return presigned_url

    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found. Please configure them in your .env file.")
        return None
    except Exception as e:
        print(f"An error occurred in image service: {e}")
        return None 