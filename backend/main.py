from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import requests
from io import BytesIO
from PIL import Image

app = FastAPI()

# Load the pre-trained model
model = load_model('../machine_learning/FoodCF.keras')

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
    19: "mango"
}

# API endpoint and API key for nutrition API
API_URL = 'https://api.api-ninjas.com/v1/nutrition'
API_KEY = 'XMlFID9DOtn1reCWUBwswg==WNa6ZlNxcWKFfDUU'

@app.post("/predict/")
async def predict_food(file: UploadFile = File(...)):
    try:
        # Read the image file
        contents = await file.read()
        img = Image.open(BytesIO(contents))
        
        # Resize the image to match the input size expected by the model
        img = img.resize((224, 224))
        
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Rescale the image

        # Predict the food item
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions[0])

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
