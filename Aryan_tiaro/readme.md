# 🚘 Tiaro Used Car Price + Pool Fare Estimator

This Streamlit application provides a powerful way to estimate the **resale price of a used car** using a machine learning stacking regression model, and then extends that by estimating **pool fare** for shared rides, while following legal guidelines to avoid commercial profits from white number plate vehicles. 

The app combines:

✅ **Machine Learning Price Prediction**  
✅ **Web-RAG** via a FastAPI backend to fetch vehicle specifications from trusted sources  
✅ **Depreciation-based Mileage Adjustment**  
✅ **Customizable Pool Fare Estimation**  

---

## ✨ Features

- **Car Resale Price Estimation**  
  - Inputs include kilometers driven, fuel type, transmission, car age, brand, and automatically fetched specs like mileage, engine, and max power from a RAG-powered FastAPI backend.

- **Fare Pooling Estimation**  
  - Calculates fair pool-based fares, adjusting for depreciation of the car so private (white plate) cars do not generate profit beyond operating costs.  
  - Incorporates fuel price, distance, number of passengers, and user-defined fare modifiers.

- **Depreciation-Based Mileage Adjustment**  
  - The app automatically caps the adjusted mileage according to vehicle segment (e.g., 23 km/l for hatchbacks) and adjusts based on resale depreciation.
  - Supports a user-controlled “Mileage Depreciation Ratio” to soften or amplify how price depreciation affects practical mileage.

- **Dynamic M2 Multiplier**  
  - Considers environment and ride-context factors like air conditioning, ride type, area surge, day type, etc.

- **Transparent UX**  
  - Shows original price, predicted resale price, and depreciation metrics in a clear panel, making it easy to understand how values were calculated.

---

## 🚀 Quickstart

1. Clone the repo.  
2. Create a `.env` file with your **GROQ_API_KEY** and **SERPER_API_KEY**:  

    ```bash
    GROQ_API_KEY=your_groq_key
    SERPER_API_KEY=your_serper_key
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Start the FastAPI backend for RAG (`fetcher_api.py`) in a separate terminal:  

    ```bash
    uvicorn fetcher_api:app --reload
    ```

5. Run Streamlit:

    ```bash
    streamlit run app.py
    ```

---

## ⚖️ Legal & Ethical Considerations

> In India, using white number plate vehicles for commercial pooling is **illegal** if a profit is made.  
>  
> Therefore, this app **enforces** that any pool fare estimated must not exceed operational cost by capping the adjusted mileage, thereby ensuring the fare does not result in profit for the car owner.  

The caps implemented are:

- **Hatchbacks:** max(23, adjusted mileage)  
- **Sedans:** max(20, adjusted mileage)  
- **SUVs:** max(16, adjusted mileage)

This makes the pooling model more legally defensible as “cost-sharing” under private vehicle usage.

---

## ⚙️ Architecture

- **Streamlit Frontend** (`app.py`)  
  - collects inputs  
  - calls the ML stacking model  
  - calls the FastAPI RAG server to pull live car specs  
  - calculates adjusted mileage, fare, and splits per passenger

- **FastAPI Backend** (`fetcher_api.py`)  
  - uses Groq LLM with a prompt to extract car specifications  
  - leverages Serper API to search top car websites  
  - returns structured JSON to the frontend

- **ML Model**  
  - Stacking Regressor trained on transformed used car prices  
  - log-transformed target to handle skew  
  - includes XGBoost, RandomForest, GradientBoosting, and Lasso in ensemble

---

## 🧩 Inputs Expected

The user must provide:

- Car brand  
- Car model  
- Variant  
- Year of purchase  
- Fuel type  
- Transmission  
- Car age  
- Kilometers driven  

and optionally fare details:

- Trip distance  
- Fuel price  
- Number of passengers  
- M2 modifier  
- Mileage depreciation ratio  
- Vehicle segment (hatchback/sedan/SUV)  
- M2 context options (air conditioning, ride type, area surge, etc.)

The app will then handle all calculations seamlessly.

---

