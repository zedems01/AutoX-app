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
import base64
from openai import OpenAI

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()



@tool
def generate_and_upload_image(prompt: str, image_name: str) -> GeneratedImage:
    """
    Generates an image using Gemini's gemini-2.5-flash-image-preview, uploads it to AWS S3,
    and returns a presigned URL.
    It includes a fallback to OpenAI's DALL-E 3 model if Gemini fails.

    Args:
        prompt (str): The prompt to generate the image from.

    Returns:
        GeneratedImage: The generated image.
    """
    image_bytes = None
    try:
        # Attempt to generate image with Gemini
        client = genai.Client()
        response = client.models.generate_content(
            model = settings.GEMINI_IMAGE_MODEL,
            contents = [prompt]
        )

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    logger.info(ctext("Image successfully generated with Gemini.", color='green'))
                    break
        
        if image_bytes is None:
            raise Exception("Gemini response did not contain image data.")

    except Exception as e:
        logger.warning(ctext(f"Gemini image generation failed: {e}. Falling back to OpenAI.", color='yellow'))
        try:
            # Fallback to OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            result = client.images.generate(
                model=settings.OPENAI_IMAGE_MODEL,
                prompt=prompt,
                size="1024x1024"
            )
            image_b64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)
            logger.info(ctext("Image successfully generated with OpenAI.", color='green'))
        except Exception as e_openai:
            logger.error(ctext(f"OpenAI image generation also failed: {e_openai}", color='red'))
            return GeneratedImage(
                is_generated=False,
                image_name="",
                local_file_path="",
                s3_url=""
            )

    try:
        images_dir = Path(__file__).resolve().parents[0] / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        image_path = images_dir / image_name

        image = Image.open(BytesIO(image_bytes))
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
        logger.error(f"An error occurred in image processing or uploading: {e}")
        return None 