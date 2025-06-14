from ..agents.state import OverallState
from ..services.image_service import generate_and_upload_image

def image_generator_node(state: OverallState) -> dict:
    """
    Generates an image based on the final prompt from the QA agent.

    Args:
        state (OverallState): The current state of the application.

    Returns:
        dict: A dictionary with the URL of the generated image.
    """
    image_prompt = state.get("final_image_prompt")
    
    if not image_prompt:
        print("No image prompt provided. Skipping image generation.")
        return {"final_image_url": None}

    print(f"Generating image with prompt: {image_prompt}")
    
    image_url = generate_and_upload_image(image_prompt)
    
    if image_url:
        print(f"Image generated and available at: {image_url}")
    else:
        print("Failed to generate or upload image.")

    return {"final_image_url": image_url} 