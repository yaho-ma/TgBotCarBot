import tempfile
from mindee import Client, product, AsyncPredictResponse
import mindee.product.driver_license
from photo_utils import make_dict_form_file
from dotenv import load_dotenv
import os


load_dotenv()
MINDEE_API_KEY = os.getenv("MINDEE_API_KEY")
mindee_client = Client(api_key=MINDEE_API_KEY)


def process_document(file_path):
    input_doc = mindee_client.source_from_path(file_path)

    # use DriverLicenseV1 model to parse documets
    result: AsyncPredictResponse = mindee_client.enqueue_and_parse(
        product.DriverLicenseV1,
        input_doc,
    )

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(str(result.document))
        temp_file_path = temp_file.name

    full_data = make_dict_form_file(temp_file_path)

    allowed_keys = [
        "Country Code",
        "State",
        "ID",
        "Category",
        "First Name",
        "Last Name",
        "Date of Birth",
        "Expiry Date",
        "Issued Date",
        "State",
        "DD Number",
    ]

    filtered_dict = {}
    for key in allowed_keys:
        if key in full_data:
            filtered_dict[key] = full_data[key]

    data_for_user = format_info_as_string(filtered_dict)

    print(data_for_user)

    return data_for_user


def format_info_as_string(info: dict) -> str:
    return "\n".join(f"{key}: {value}" for key, value in info.items())
