import base64
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from openai import OpenAI
from ...config import settings
from langchain_core.tools import tool
from .schemas import GeneratedImage
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



@tool
def generate_and_upload_image(prompt: str, image_name: str) -> GeneratedImage:
    """
    Generates an image using OpenAI's gpt-image-1, uploads it to AWS S3,
    and returns a presigned URL.

    Args:
        prompt (str): The prompt to generate the image from.

    Returns:
        GeneratedImage: The generated image.
    """
    try:
        # 1. Generate the image with OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        image_b64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)

        image_key = f"images/{image_name}"

        # Define the base directory for images
        images_dir = Path("images")
        # Ensure the directory exists, create if not
        images_dir.mkdir(parents=True, exist_ok=True)
        # Define the full path for the image file
        image_path = images_dir / image_name

        bucket_name = settings.BUCKET_NAME

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Image saved to {image_path}")
        
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
            ExpiresIn=3600
        )
        
        logger.info(f"Successfully uploaded image {image_name} to S3 bucket {bucket_name}.")
        return GeneratedImage(
            image_name=image_name,
            local_file_path=image_path,
            s3_url=presigned_url
        )

    except (NoCredentialsError, PartialCredentialsError):
        logger.error("AWS credentials not found. Please configure them in your .env file.")
        return None
    except Exception as e:
        logger.error(f"An error occurred in image service: {e}")
        return None 