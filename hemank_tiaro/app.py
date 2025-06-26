import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")  
SERPER_API_KEY = os.getenv("SERPER_API_KEY")            

# --- FUNCTION TO GET TOP RESULT FROM SERPER ---
def get_top_result_url(query):
    headers = {"X-API-KEY": SERPER_API_KEY}
    payload = {"q": query + " site:cardekho.com"}
    
    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
        results = response.json()
        if "organic" in results and results["organic"]:
            return results["organic"][0]["link"]
    except Exception as e:
        return f"Error in Serper: {e}"
    
    return None

# --- FUNCTION TO FETCH PAGE CONTENT ---
def fetch_page_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text(separator=' ')
    except Exception as e:
        return f"Error fetching page: {e}"

def extract_car_info_with_groq(text_content):
    llm = ChatGroq(model_name="Gemma2-9b-It", temperature=0)
    
    prompt = ChatPromptTemplate.from_template("""
You are a car expert assistant. From the given car page content, extract and return the following fields in JSON:
- original_price (in ₹) (on-road price)
- company_claimed_mileage (in km/l)

Only respond with valid JSON with exactly those two fields.

Page Content:
{text}
""")
    
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.invoke({"text": text_content[:4000]})
    return result['text']

def get_car_info_online(car_name, model, year, fuel_type, variant):
    query = f"{car_name} {model} {year} {fuel_type} {variant}"
    url = get_top_result_url(query)
    if not url or "Error" in url:
        return {"error": "No search result found or Serper failed."}
    
    page_text = fetch_page_content(url)
    if "Error fetching page" in page_text:
        return {"error": page_text}
    
    result = extract_car_info_with_groq(page_text)
    return result

st.set_page_config(page_title="Car Info RAG App", page_icon="🚗")
st.title("🚗 Car Info Fetcher using RAG + Groq (Serper Version)")

with st.form("car_form"):
    col1, col2 = st.columns(2)
    car_name = col1.text_input("Car Brand", placeholder="e.g., Hyundai")
    model = col2.text_input("Model", placeholder="e.g., Creta")

    col3, col4 = st.columns(2)
    year = col3.text_input("Year", placeholder="e.g., 2021")
    fuel_type = col4.selectbox("Fuel Type", ["petrol", "diesel", "CNG", "electric"])

    variant = st.text_input("Variant", placeholder="e.g., SX")

    submitted = st.form_submit_button("🔍 Search")

if submitted:
    if not all([car_name, model, year, fuel_type, variant]):
        st.error("Please fill in all fields.")
    else:
        with st.spinner("Fetching data..."):
            response = get_car_info_online(car_name, model, year, fuel_type, variant)
        
        st.subheader("📦 Retrieved Info")
        st.code(response, language='json')
