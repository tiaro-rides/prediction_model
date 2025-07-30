from fastapi import FastAPI
from pydantic import BaseModel
import pickle
from fastapi.middleware.cors import CORSMiddleware

# Initialize app
app = FastAPI()

# CORS settings (important for Streamlit to interact with this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained ML model
try:
    with open("fare_model.pkl", "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Pydantic input model
class FareInput(BaseModel):
    trip_distance_km: float
    claimed_mileage_kmpl: float
    fuel_price_per_litre: float
    vehicle_age: int

# Root route
@app.get("/")
def read_root():
    return {"message": "Fare & Mileage Predictor API is working ✅"}

# Prediction route
@app.post("/predict_fare")
def predict_fare(data: FareInput):
    if not model:
        return {"error": "❌ Model not loaded"}

    try:
        # Prepare input for prediction
        input_features = [[
            data.trip_distance_km,
            data.claimed_mileage_kmpl,
            data.fuel_price_per_litre,
            data.vehicle_age
        ]]

        prediction = model.predict(input_features)[0]

        # Calculate total estimated fare
        fuel_needed = data.trip_distance_km / data.claimed_mileage_kmpl
        estimated_fare = round(fuel_needed * data.fuel_price_per_litre)

        return {
            "predicted_mileage": round(prediction, 2),
            "estimated_fare": estimated_fare
        }
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}

