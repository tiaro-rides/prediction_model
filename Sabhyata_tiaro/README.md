# Fare and Mileage Prediction

This project is a machine learning-based fare and mileage prediction system designed for Tiaro Rides. It uses car and trip attributes to calculate estimated fuel cost and final fare using a rule-based multiplier model.

---

## 🚀 Features

- Predicts ride fare based on vehicle, ride, and fuel data.
- Real-time Streamlit UI for inputs and live predictions.
- Handles surge pricing, car type, ride type, time-based demand, and more.
- Dataset-ready for future model training.

---

## 📊 Prediction Formula

### 📌 Fare = (Distance / Mileage) × Fuel_Price × M2

Where:
- `(Distance / Mileage) × Fuel_Price` = raw fuel cost
- `M2` = multiplier based on vehicle + ride + demand context

---

### 🧮 M2 Calculation Factors

| Factor           | Impact on M2            | Suggested Values                 |
|------------------|--------------------------|----------------------------------|
| Vehicle Age      | Penalize older cars      | 1.0 → 0.7 (linearly by age)      |
| Air Conditioning | Adds small premium       | ON: 1.05, OFF: 1.0               |
| Ride Type        | Shared vs Exclusive      | Shared: 1.0, Exclusive: 1.2      |
| Car Type         | Comfort level            | Hatch: 1.0, Sedan: 1.1, SUV: 1.2 |
| Time of Day      | Rush hour impact         | Normal: 1.0, Rush: 1.1–1.3       |
| Day Type         | Weekend premium          | Weekday: 1.0, Weekend: 1.1       |
| Area Surge       | Supply-demand modifier   | ± 0.1                            |

> Example M2 = 0.9 × 1.05 × 1.2 × 1.2 × 1.1 + 0.1 ≈ 1.6

---

## 📁 Project Structure


Sabhyata_tiaro/
│
├── Fare and Mileage Prediction.ipynb # Notebook for model and UI logic
├── fare_prediction_dataset.csv # Input dataset with trip & car details
├── streamlit-app-2025-06-30-20-06-73.webm # Demo recording of app usage
├── ngrok_recovery_codes.txt # Ngrok token backup (optional)
├── README.md 



---

## 🧾 Sample Dataset Columns

| Column                 | Type        | Description                            | Example      |
|------------------------|-------------|----------------------------------------|--------------|
| `trip_distance_km`     | Numeric     | Trip distance in km                    | 10           |
| `claimed_mileage_kmpl`| Numeric     | Vehicle's mileage                      | 18           |
| `fuel_price_per_litre`| Numeric     | Local fuel price                       | 90           |
| `car_brand`            | Categorical | Brand for ML                           | Hyundai      |
| `year_of_manufacture` | Numeric     | For calculating car age                | 2017         |
| `kms_driven`           | Numeric     | To estimate depreciation               | 45000        |
| `car_type`             | Categorical | Hatch/Sedan/SUV                        | SUV          |
| `ride_type`            | Categorical | Shared/Exclusive                       | Exclusive    |
| `AC_on`                | Boolean     | AC status                              | TRUE         |
| `time_of_day`          | Categorical | Morning/Evening etc.                   | Evening      |
| `day_type`             | Categorical | Weekday/Weekend                        | Weekend      |
| `area_supply_status`   | Categorical | Demand level                           | Low          |
| `resale_value`         | Numeric     | For M1 price model                     | 1000000      |
| `actual_fare_paid`     | Numeric     | Real fare paid (optional for training) | 93.36        |

---

## 💻 How to Run

1. **Navigate to the project folder:**

```bash
cd Sabhyata_tiaro

2. **Install dependencies:

'''bash
pip install streamlit pandas scikit-learn

3. **Launch Streamlit app:

'''bash
streamlit run "Fare and Mileage Prediction.ipynb"

🌐 Ngrok Access (Optional)

'''bash
ngrok http 8501


