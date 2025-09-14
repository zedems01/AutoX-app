# TODO:
# * refine the logic of the image_generator node to handle image edits from user feedbacks


from functools import cache
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from ..config import settings
from langchain_core.tools import tool
from .schemas import GeneratedImage
from pathlib import Path

from google import genai
from PIL import Image
from io import BytesIO

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()



@tool
def generate_and_upload_image(prompt: str, image_name: str) -> GeneratedImage:
    """
    Generates an image using Gemini's gemini-2.5-flash-image-preview, uploads it to AWS S3,
    and returns a presigned URL.

    Args:
        prompt (str): The prompt to generate the image from.

    Returns:
        GeneratedImage: The generated image.
    """
    try:

        images_dir = Path(__file__).resolve().parents[0] / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        image_path = images_dir / image_name

        client = genai.Client()
        response = client.models.generate_content(
            model = settings.GEMINI_IMAGE_MODEL,
            contents = [prompt]
        )

        if response.candidates[0].content == None:
            return GeneratedImage(
                is_generated=False,
                image_name="",
                local_file_path="",
                s3_url=""
            )
        else:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(image_path, 'JPEG', optimize=True, quality=95)

            relative_path = image_path.relative_to(Path(__file__).resolve().parents[0])
            logger.info(ctext(f"Image saved to {str(relative_path)}", color='white'))
            
            # Upload the image to AWS S3 to get a presigned URL
            bucket_name = settings.BUCKET_NAME
            image_key = f"images/{image_name}"

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
                is_generated=True,
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