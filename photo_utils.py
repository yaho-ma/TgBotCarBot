import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def save_user_photo(photo, bot) -> str:

    try:
        os.makedirs("downloads", exist_ok=True)

        if not photo:
            logger.error("No photo found in the list.")
            return "Error: No photo received."  

        # Get the highest quality photo (last in the list)
        best_photo = photo[-1]
        try:
            file = await bot.get_file(best_photo.file_id)
        except Exception as e:
            logger.error(f"Failed to get file from bot: {e}")
            return "Error: Failed to retrieve the photo from Telegram servers."

        # File path, create folder if it does not exist
        file_path = f"downloads/{best_photo.file_unique_id}.jpg"

        try:
            # Download the photo to disk
            await file.download_to_drive(file_path)
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return "Error: Could not download the file to disk."
        
        logger.info(f"Photo saved to {file_path}")

        return file_path
    
    except Exception as e:
        logger.exception(f"Unexpected error in save_user_photo: {e}")
        return "Error: An unexpected error occurred while saving the photo."


# make dictionary form file
def make_dict_form_file(file_path):
    data = {}

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {}
    
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line == "Prediction":
                    continue
                if line.startswith(":") and ":" in line[1:]:
                    # Split only on the second colon
                    parts = line.split(":", 2)
                    key = parts[1].strip()
                    value = parts[2].strip() if len(parts) > 2 else ""
                    data[key] = value
    except Exception as e:
        logger.error(f"Error reading from file {file_path}: {e}")
        return {}
    return data
