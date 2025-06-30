import streamlit as st
import pandas as pd
import requests
import pickle
import json
import numpy as np
import re

# --- Extract float from mixed string ---


def extract_number(value):
    match = re.search(r"\d+\.?\d*", str(value))
    return float(match.group()) if match else None

# --- Calculate Fare ---


def calculate_fare(distance, mileage, fuel_price, original_price, predicted_price, m2, passengers):
    if mileage == 0 or original_price == 0 or passengers == 0:
        return None, None
    m1 = 1 + (1 - (predicted_price * 0.9 / original_price))
    total_fare = (distance / mileage) * fuel_price * m1 * m2
    per_head_fare = total_fare / passengers
    return round(total_fare, 2), round(per_head_fare, 2)


# --- Load model and car list ---
with open("stacking_model.pkl", "rb") as f:
    price_model = pickle.load(f)
    st.write(f"✅ Model type loaded: {type(price_model)}")

with open("car_brand_names.pkl", "rb") as f:
    car_brand_names = pickle.load(f)

# --- Page layout ---
st.set_page_config(page_title="Used Car Price + Fare Predictor", page_icon="🚗")
st.title("🚘 Used Car Price + Pool Fare Estimator")

st.markdown("Enter car details to predict price and estimate pooled ride fare.")

# --- API Inputs ---
st.subheader("🔍 Basic Car Info (for API)")
col1, col2 = st.columns(2)
car_name = col1.selectbox("Car Brand Name", options=car_brand_names)
model_name = col2.text_input("Model", placeholder="e.g. Swift")

col3, col4 = st.columns(2)
year = col3.text_input("Year of Purchase", placeholder="e.g. 2020")
variant = col4.text_input("Variant", placeholder="e.g. VXI")

fuel_type = st.selectbox("Fuel Type", ["petrol", "diesel", "CNG", "electric"])

# --- Car Type for adjusted mileage logic ---
car_type = st.selectbox("Car Type", ["Hatchback", "Sedan", "SUV"])

# --- Manual Inputs ---
st.subheader("🛠️ Manual Inputs")
col5, col6 = st.columns(2)
km_driven = col5.number_input("Kilometers Driven", min_value=0)
transmission = col6.selectbox("Transmission Type", ["manual", "automatic"])
car_age = st.slider("Car Age (years)", min_value=0, max_value=30)

# --- Fare Inputs ---
st.subheader("💸 Fare Estimation Inputs")
col7, col8 = st.columns(2)
distance = col7.number_input("Trip Distance (in km)", min_value=1)
fuel_price = col8.number_input(
    "Current Fuel Price (₹/liter)", min_value=50.0, value=100.0)

col9, col10 = st.columns(2)
num_passengers = col9.number_input(
    "Number of Passengers", min_value=1, value=2)
m2 = col10.number_input("Fare Modifier (M2)",
                        min_value=0.1, value=1.0, step=0.1)

custom_depreciation_ratio = st.slider(
    "Mileage Depreciation Ratio (0 = ignore price depreciation, 1 = full proportional)",
    min_value=0.0,
    max_value=1.0,
    value=1.0,
    step=0.05
)

# --- Submit Button ---
if st.button("🔮 Predict Price & Estimate Fare"):
    if not all([car_name, model_name, year, fuel_type, variant]):
        st.warning("🚨 Please fill all fields.")
    else:
        with st.spinner("⏳ Fetching car specs..."):
            api_payload = {
                "car_name": car_name,
                "model": model_name,
                "year": str(year),
                "fuel_type": fuel_type,
                "variant": variant
            }

            try:
                response = requests.post(
                    "http://127.0.0.1:8000/get-car-info", json=api_payload)
                result = response.json()

                if "error" in result:
                    st.error(f"❌ API Error: {result['error']}")
                else:
                    data = result["result"]

                    # Extract values safely
                    mileage = extract_number(
                        data.get("company_claimed_mileage", ""))
                    engine = extract_number(data.get("engine", ""))
                    max_power = extract_number(data.get("max_power", ""))
                    original_price = extract_number(
                        data.get("original_price", ""))

                    if None in (mileage, engine, max_power, original_price):
                        st.error("⚠️ Missing data. Try another input or car.")
                    else:
                        input_df = pd.DataFrame([{
                            "km_driven": km_driven,
                            "fuel": fuel_type,
                            "transmission": transmission,
                            "mileage": mileage,
                            "engine": engine,
                            "max_power": max_power,
                            "car_brand_name": car_name,
                            "car_age": car_age
                        }])

                        st.write("🔍 Model Input Preview:")
                        st.dataframe(input_df)

                        # Predict log price and reverse log
                        predicted_log = price_model.predict(input_df)[0]
                        predicted_price = np.expm1(predicted_log)

                        st.success(
                            f"💰 Predicted Resale Price: ₹{predicted_price*0.9:,.2f}")
                        st.info(
                            f"🧾 Original On-Road Price: ₹{original_price:,.2f}")

                        # --- Depreciation Analysis ---
                        depreciated_value = original_price - predicted_price
                        depreciation_percent = (
                            depreciated_value / original_price) * 100
                        retained_percent = (
                            predicted_price / original_price) * 100

                        st.subheader("📉 Car Depreciation Analysis")
                        colA, colB, colC = st.columns(3)
                        colA.metric("Original Price",
                                    f"₹{original_price:,.0f}")
                        colB.metric("Predicted Price",
                                    f"₹{predicted_price:,.0f}")
                        colC.metric(
                            "Depreciated Value", f"₹{depreciated_value:,.0f}", f"-{depreciation_percent:.1f}%")

                        st.caption(
                            f"⚖️ Retained Value: **{retained_percent:.2f}%** of original on-road price.")
                        st.progress(min(retained_percent / 100, 1.0))

                        # --- Adjusted Mileage Calculation ---
                        m1_raw = 1 + (1 - (predicted_price * 0.9 / original_price))
                        m1 = 1 + custom_depreciation_ratio * (m1_raw - 1)
                        adjusted_mileage = mileage / m1 if m1 != 0 else None

                        # Apply caps
                        if adjusted_mileage:
                            if car_type == "SUV":
                                capped_mileage = max(16, adjusted_mileage)
                            elif car_type == "Sedan":
                                capped_mileage = max(20, adjusted_mileage)
                            elif car_type == "Hatchback":
                                capped_mileage = max(23, adjusted_mileage)
                            else:
                                capped_mileage = adjusted_mileage  # fallback
                            st.info(
                                f"📉 Adjusted Mileage (Based on Depreciation + Cap for {car_type}): **{capped_mileage:.2f} km/l**")
                        else:
                            st.warning(
                                "⚠️ Could not compute adjusted mileage due to invalid values.")

                        # --- Fare Calculation ---
                        total_fare, per_head = calculate_fare(
                            distance, capped_mileage, fuel_price, original_price, predicted_price, m2, num_passengers
                        )

                        if total_fare:
                            st.subheader("🚕 Estimated Pool Fare")
                            st.write(f"**Total Fare**: ₹{total_fare:,.2f}")
                            st.write(
                                f"**Per Passenger (Split)**: ₹{per_head:,.2f}")
                        else:
                            st.warning(
                                "Could not compute fare due to invalid values.")

            except Exception as e:
                st.error(f"❌ Error during prediction: {e}")
