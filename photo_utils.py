import os


async def save_user_photo(photo, bot) -> str:
    os.makedirs("downloads", exist_ok=True)

    # Get the highest quality photo (last in the list)
    best_photo = photo[-1]
    file = await bot.get_file(best_photo.file_id)

    # File path, create folder if it does not exist
    file_path = f"downloads/{best_photo.file_unique_id}.jpg"

    # Download the photo to disk
    await file.download_to_drive(file_path)

    return file_path


# make dictionary form file
def make_dict_form_file(file_path):
    data = {}
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
    return data
