# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

class FareInput(BaseModel):
    trip_distance_km: float
    claimed_mileage_kmpl: float
    fuel_price_per_litre: float
    vehicle_age: int
    car_type: str
    ride_type: str

# Load model
try:
    model = joblib.load("fare_model.joblib")
except Exception:
    model = None

@app.get("/")
def root():
    return {"message": "✅ Fare & Mileage API is live"}

@app.post("/predict_fare")
def predict_fare(data: FareInput):
    try:
        if model is None:
            raise ValueError("Model not loaded")

        # Encode car & ride type
        car_map = {"Hatch": 1.0, "Sedan": 1.1, "SUV": 1.2}
        ride_map = {"Shared": 1.0, "Exclusive": 1.2}

        car_type_factor = car_map.get(data.car_type, 1.0)
        ride_type_factor = ride_map.get(data.ride_type, 1.0)

        input_features = np.array([[data.vehicle_age, 1.2, ride_type_factor, car_type_factor, 1.0]])
        predicted_mileage = model.predict(input_features)[0]

        fuel_used = data.trip_distance_km / predicted_mileage
        base_fare = fuel_used * data.fuel_price_per_litre
        final_fare = max(40, base_fare)

        return {
            "predicted_mileage": round(predicted_mileage, 2),
            "fare_estimate": round(final_fare, 2)
        }

    except Exception as e:
        return {"error": f"❌ Prediction error: {str(e)}"}

