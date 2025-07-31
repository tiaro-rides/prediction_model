from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

app = FastAPI()

# ✅ Simulate training
np.random.seed(42)
n = 500
train_df = pd.DataFrame({
    'vehicle_age': np.random.randint(0, 20, n),
    'ac_factor': np.full(n, 1.2),
    'ride_type_factor': np.random.choice([1.0, 1.2], n),
    'car_type_factor': np.random.choice([1.0, 1.1, 1.2], n),
    'time_of_day_factor': np.full(n, 1.0)
})

train_df['mileage'] = (
    21
    - 0.5 * train_df['vehicle_age']
    - 2.0 * (train_df['ac_factor'] - 1.0)
    - 1.5 * (train_df['car_type_factor'] - 1.0)
    - 1.0 * (train_df['ride_type_factor'] - 1.0)
    - 0.5 * (train_df['time_of_day_factor'] - 1.0)
    + np.random.normal(0, 0.5, n)
).clip(lower=8, upper=25)

model = LinearRegression()
model.fit(train_df[['vehicle_age', 'ac_factor', 'ride_type_factor', 'car_type_factor', 'time_of_day_factor']], train_df['mileage'])


class FareInput(BaseModel):
    trip_distance_km: float
    fuel_price_per_litre: float
    vehicle_age: int
    car_type: str  # "Hatch", "Sedan", "SUV"
    ride_type: str  # "Shared" or "Exclusive"


@app.get("/")
def root():
    return {"message": "✅ Fare & Mileage API is live"}


@app.post("/predict")
def predict_fare(data: FareInput):
    # Convert input to model factors
    ac_factor = 1.2
    ride_type_factor = 1.0 if data.ride_type == "Shared" else 1.2
    car_type_factor = {"Hatch": 1.0, "Sedan": 1.1, "SUV": 1.2}.get(data.car_type, 1.0)
    time_of_day_factor = 1.0

    input_df = pd.DataFrame([{
        "vehicle_age": data.vehicle_age,
        "ac_factor": ac_factor,
        "ride_type_factor": ride_type_factor,
        "car_type_factor": car_type_factor,
        "time_of_day_factor": time_of_day_factor
    }])

    # Predict mileage
    predicted_mileage = float(model.predict(input_df)[0])
    predicted_mileage = float(np.clip(predicted_mileage, 8.0, 22.0))

    # Fare calculation
    fuel_used = data.trip_distance_km / predicted_mileage
    base_fare = fuel_used * data.fuel_price_per_litre
    final_fare = max(40, base_fare)

    return {
        "predicted_mileage": round(predicted_mileage, 2),
        "fare_estimate": round(final_fare, 2)
    }

