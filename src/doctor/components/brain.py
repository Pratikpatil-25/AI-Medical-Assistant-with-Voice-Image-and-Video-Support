import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from google import genai
from langchain_core.messages import HumanMessage
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
from pathlib import Path
import time
from constants import prompt
from config import params


load_dotenv()

# here we are going to use ChatGoogleGenerativeAI for text and image inputs but for video inputs we will use Google's official SDK genai.
# well, we can use ChatGoogleGenerativeAI for videos as well but in case of large inputs, the way how large media files are uploaded and managed isn't that good in case of langchain-google-genai
# and as we are going to convert the input (only image and video) into base64 format, the input gets larger i.e. to few 100 MBs



def doctor( patient_query, image_filepath : str| None = None, video_filepath : str | None = None):

    model_prompt = prompt(patient_query)


    if video_filepath:
        video_path = Path(video_filepath)

        client = genai.Client()

        video_file = client.files.upload(
            file=video_path
        )

        # Wait until processing completes
        while video_file.state.name == "PROCESSING":
            print("Processing video...")
            time.sleep(2)

            video_file = client.files.get(
                name=video_file.name
            )

        if video_file.state.name != "ACTIVE":
            raise RuntimeError(
                f"Video processing failed. State={video_file.state.name}"
            )

        else :
            print("Video ready!")

        vid_response = client.models.generate_content(
            model=params["gemini_model"],
            contents=[
                video_file,
                model_prompt
            ]
        )

        return vid_response.text

    elif image_filepath : 
        llm = ChatGoogleGenerativeAI(model = params.gemini_model, temperature = params["temperature"])

        image = Image.open(image_filepath)

        image.thumbnail((1024,1024))

        buffer = BytesIO()

        image.convert("RGB").save(buffer, format = "JPEG", quality = 75)

        image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        message = HumanMessage(
            content= [{
                "type" : "text",
                "text" : model_prompt
            },
            {
                "type": "image_url",
                "image_url": { "url" : f"data:image/jpeg;base64, {image_data}" }
            }]
        )

        img_response = llm.invoke([message])

        return img_response.content


    else:
        raise ValueError(
            "Either image_filepath or video_filepath must be provided."
        )


