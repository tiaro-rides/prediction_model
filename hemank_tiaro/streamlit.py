import streamlit as st
import numpy as np
import pickle
import pandas as pd     
import ast
from app import get_car_info_online
import re

with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

fuel_type_mapping = {'CNG': 0, 'Diesel': 1, 'Petrol': 2}
transmission_mapping = {'Automatic': 0, 'Manual': 1}
seller_type_mapping = {'Dealer': 0, 'Individual': 1}

car_name_mapping = {'800': 0, 'Activa 3g': 1, 'Activa 4g': 2, 'Bajaj  ct 100': 3, 'Bajaj Avenger 150': 4,
                    'Bajaj Avenger 150 street': 5, 'Bajaj Avenger 220': 6, 'Bajaj Avenger 220 dtsi': 7,
                    'Bajaj Avenger Street 220': 8, 'Bajaj Discover 100': 9, 'Bajaj Discover 125': 10,
                    'Bajaj Dominar 400': 11, 'Bajaj Pulsar  NS 200': 12, 'Bajaj Pulsar 135 LS': 13,
                    'Bajaj Pulsar 150': 14, 'Bajaj Pulsar 220 F': 15, 'Bajaj Pulsar NS 200': 16,
                    'Bajaj Pulsar RS200': 17, 'Hero  CBZ Xtreme': 18, 'Hero  Ignitor Disc': 19,
                    'Hero Extreme': 20, 'Hero Glamour': 21, 'Hero Honda CBZ extreme': 22,
                    'Hero Honda Passion Pro': 23, 'Hero Hunk': 24, 'Hero Passion Pro': 25,
                    'Hero Passion X pro': 26, 'Hero Splender Plus': 27, 'Hero Splender iSmart': 28,
                    'Hero Super Splendor': 29, 'Honda Activa 125': 30, 'Honda Activa 4G': 31,
                    'Honda CB Hornet 160R': 32, 'Honda CB Shine': 33, 'Honda CB Trigger': 34,
                    'Honda CB Unicorn': 35, 'Honda CB twister': 36, 'Honda CBR 150': 37,
                    'Honda Dream Yuga ': 38, 'Honda Karizma': 39, 'Hyosung GT250R': 40, 'KTM 390 Duke ': 41,
                    'KTM RC200': 42, 'KTM RC390': 43, 'Mahindra Mojo XT300': 44,
                    'Royal Enfield Bullet 350': 45, 'Royal Enfield Classic 350': 46,
                    'Royal Enfield Classic 500': 47, 'Royal Enfield Thunder 350': 48,
                    'Royal Enfield Thunder 500': 49, 'Suzuki Access 125': 50, 'TVS Apache RTR 160': 51,
                    'TVS Apache RTR 180': 52, 'TVS Jupyter': 53, 'TVS Sport ': 54, 'TVS Wego': 55,
                    'UM Renegade Mojave': 56, 'Yamaha FZ  v 2.0': 57, 'Yamaha FZ 16': 58, 'Yamaha FZ S ': 59,
                    'Yamaha FZ S V 2.0': 60, 'Yamaha Fazer ': 61, 'alto 800': 62, 'alto k10': 63,
                    'amaze': 64, 'baleno': 65, 'brio': 66, 'camry': 67, 'ciaz': 68, 'city': 69,
                    'corolla': 70, 'corolla altis': 71, 'creta': 72, 'dzire': 73, 'elantra': 74,
                    'eon': 75, 'ertiga': 76, 'etios cross': 77, 'etios g': 78, 'etios gd': 79,
                    'etios liva': 80, 'fortuner': 81, 'grand i10': 82, 'i10': 83, 'i20': 84,
                    'ignis': 85, 'innova': 86, 'jazz': 87, 'land cruiser': 88, 'omni': 89, 'ritz': 90,
                    's cross': 91, 'swift': 92, 'sx4': 93, 'verna': 94, 'vitara brezza': 95,
                    'wagon r': 96, 'xcent': 97}

st.title('Car Selling Price Prediction')

car_name = st.selectbox('Car Name', list(car_name_mapping.keys()))
year = st.number_input('Year of Purchase', min_value=2000, max_value=2025, step=1)
present_price = st.number_input('Present Price (in Lakhs)', min_value=0.0, step=0.1)
kms_driven = st.number_input('Kms Driven', min_value=0, step=500)

fuel_type = st.selectbox('Fuel Type', list(fuel_type_mapping.keys()))
seller_type = st.selectbox('Seller Type', list(seller_type_mapping.keys()))
transmission = st.selectbox('Transmission Type', list(transmission_mapping.keys()))

if st.button('Predict Selling Price'):
    input_data = [
        car_name_mapping[car_name],
        year,
        present_price,
        scaler.transform([[kms_driven]])[0][0],
        fuel_type_mapping[fuel_type],
        seller_type_mapping[seller_type],
        transmission_mapping[transmission]
    ]

    input_df = pd.DataFrame([input_data], columns=['Car_Name', 'Year', 'Present_Price', 'Kms_Driven',
                                                   'Fuel_Type', 'Seller_Type', 'Transmission'])

    predicted_price = model.predict(input_df)

    st.success(f'Predicted Selling Price: {predicted_price[0]:.2f} Lakhs')

    value = get_car_info_online(car_name, car_name, year, fuel_type, "a")
    st.success(value)

    all_numbers = re.findall(r"[\d.]+", value)

    if len(all_numbers) == 3:
        lower_limit_value = float(all_numbers[1])  # Lower limit of the price range
        mileage = float(all_numbers[2])  # In case you only want the first mileage 
    else:
        lower_limit_value = float(all_numbers[1])
        mileage = float(all_numbers[3])

    percentage_depreciation = 100- (predicted_price/lower_limit_value * 100)

    st.success(f'Predicted Depreciation in value is %{percentage_depreciation[0]:.2f}')


    final_dec_mil = mileage - ((5/10)*(percentage_depreciation[0]/100)) * mileage   

    st.success(f"Company claimed mileage {mileage:.2f}km/L")
    st.success(f"Predicted Depreciated claimed mileage {final_dec_mil:.2f}km/L")

    