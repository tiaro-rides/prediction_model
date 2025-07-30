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
    vehicle_age = st.slider("Vehicle Age (in years)", 0, 20, 1)

    submitted = st.form_submit_button("Calculate Fare")

# When form is submitted
if submitted:
    payload = {
        "trip_distance_km": float(trip_distance),
        "claimed_mileage_kmpl": float(claimed_mileage),
        "fuel_price_per_litre": float(fuel_price),
        "vehicle_age": int(vehicle_age)
    }

    try:
        response = requests.post(
            "https://fare-api.onrender.com/predict_fare",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            st.success(f"🎯 Predicted Mileage: {data['predicted_mileage']} km/l")
            st.success(f"�� Estimated Fare: ₹{data['estimated_fare']}")
        elif response.status_code == 422:
            st.error("Error 422: Invalid input format. Please check your values.")
        else:
            st.error(f"Error {response.status_code}: Something went wrong.")

    except requests.exceptions.RequestException as e:
        st.error("🚨 Failed to connect to backend API.")
        st.text(str(e))

