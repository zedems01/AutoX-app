import base64
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from openai import OpenAI
from ..config import settings
from langchain_core.tools import tool
from .schemas import GeneratedImage
from pathlib import Path

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()



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
        # Generate the image with OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        image_b64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)

        image_key = f"images/{image_name}"

        # Define the path to the frontend's public/images directory
        # images_dir = Path(__file__).resolve().parents[3] / "frontend" / "public" / "images"
        images_dir = Path(__file__).resolve().parents[0] / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        image_path = images_dir / image_name

        bucket_name = settings.BUCKET_NAME

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        # logger.info(ctext(f"Image saved to {str(image_path)}", color='white'))
        # relative_path = image_path.relative_to(Path(__file__).resolve().parents[3])
        relative_path = image_path.relative_to(Path(__file__).resolve().parents[0])
        logger.info(ctext(f"Image saved to {str(relative_path)}", color='white'))
        
        # Upload the image to AWS S3 to get a presigned URL
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
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': image_key},
            ExpiresIn=3600
        )
        
        logger.info(ctext(f"Successfully uploaded image {image_name} to S3 bucket {bucket_name}.", color='white'))
        return GeneratedImage(
            image_name=image_name,
            local_file_path=str(image_path),
            s3_url=presigned_url
        )

    except (NoCredentialsError, PartialCredentialsError):
        logger.error("AWS credentials not found. Please configure them in your .env file.")
        return None
    except Exception as e:
        logger.error(f"An error occurred in image service: {e}")
        return None 