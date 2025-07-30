import streamlit as st
import requests

st.set_page_config(page_title="Fare & Mileage Predictor", page_icon="🚗")
st.title("🚗 Fare & Mileage Predictor")
st.caption("Powered by FastAPI • Deployed on Render")

# Input Form
with st.form("fare_form"):
    trip_distance = st.number_input("Trip Distance (in km)", min_value=1.0)
    claimed_mileage = st.number_input("Claimed Mileage (in km/l)", min_value=1.0)
    fuel_price = st.number_input("Fuel Price (₹/L)", min_value=1.0)
    vehicle_age = st.slider("Vehicle Age (in years)", min_value=0, max_value=20, value=2)

    car_type = st.selectbox("Car Type", ["Hatch", "Sedan", "SUV"])
    ride_type = st.radio("Ride Type", ["Exclusive", "Shared"])

    form_submit_button = st.form_submit_button(label="Predict")

    if form_submit_button:
        try:
            data = {
                "trip_distance_km": trip_distance,
                "claimed_mileage_kmpl": claimed_mileage,
                "fuel_price_per_litre": fuel_price,
                "vehicle_age": vehicle_age,
                "car_type": car_type,
                "ride_type": ride_type
            }

            response = requests.post(
                "https://fare-api-npue.onrender.com/predict_fare",
                json=data
            )
            result = response.json()

            if "error" in result:
                st.error(result["error"])
            else:
                st.success("🎯 Prediction Successful!")
                st.metric("Predicted Mileage", f'{result["predicted_mileage"]} km/l')
                st.metric("Estimated Fare", f'₹ {result["fare_estimate"]}')
        except Exception as e:
            st.error(f"❌ Request failed: {e}")

