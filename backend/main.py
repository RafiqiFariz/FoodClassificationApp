import os
import sys
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the pre-trained model
model_path = os.path.abspath('../machine_learning/FoodCF.keras')
model = load_model(model_path)

# Define your food labels based on the provided list
food_labels = {
    0: "apple",
    1: "banana",
    2: "beetroot",
    3: "bell pepper",
    4: "cabbage",
    5: "capsicum",
    6: "carrot",
    7: "cauliflower",
    8: "chilli pepper",
    9: "corn",
    10: "cucumber",
    11: "eggplant",
    12: "garlic",
    13: "ginger",
    14: "grapes",
    15: "jalepeno",
    16: "kiwi",
    17: "lemon",
    18: "lettuce",
    19: "mango",
    20: "onion",
    21: "orange",
    22: "paprika",
    23: "pear",
    24: "peas",
    25: "pineapple",
    26: "pomegranate",
    27: "potato",
    28: "raddish",
    29: "soy beans",
    30: "spinach",
    31: "sweetcorn",
    32: "sweetpotato",
    33: "tomato",
    34: "turnip",
    35: "watermelon",
}

API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')


@app.get("/")
def index():
    return {
        "name": "Food Recognition API",
        "version": "1.0",
        "status": 200
    }


@app.post("/predict")
async def predict_food(file: UploadFile = File(...)):
    try:
        # Read the image file
        contents = await file.read()
        img = Image.open(BytesIO(contents)).convert('RGB')  # Convert image to RGB
        
        # Resize the image to match the input size expected by the model
        img = img.resize((224, 224))

        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Rescale the image

        # Predict the food item
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions[0])
        max_probability = np.max(predictions[0])

        # Set a threshold for the confidence level
        confidence_threshold = 0.5

        # Check if the highest probability is below the threshold
        if max_probability < confidence_threshold:
            return JSONResponse(status_code=404, content={
                "status": "error",
                "message": "Food item not recognized."
            })

        # Map the predicted class to the food name
        food_name = food_labels.get(predicted_class, "Unknown")

        if food_name == "Unknown":
            return JSONResponse(status_code=404, content={
                "status": "error",
                "message": "Food item not recognized."
            })

        # Get calorie information from the nutrition API
        calories = get_calories_from_api(food_name)
        if not calories:
            return JSONResponse(status_code=404, content={
                "status": "error",
                "message": "Calorie information not found."
            })

        return {
            "status": "success",
            "message": "Food item recognized successfully.",
            "food_name": food_name,
            "nutrition": calories[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_calories_from_api(food_name):
    try:
        query = f'{food_name} calories'
        api_url = f'{API_URL}?query={query}'
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
        if response.status_code == requests.codes.ok:
            data = response.json()
            return data
    except Exception as e:
        print(f"Error while querying API: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
