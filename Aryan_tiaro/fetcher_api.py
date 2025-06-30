from fastapi import FastAPI
import json
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

app = FastAPI(title="Car Info RAG API")

# --- Serper search function ---
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

# --- Web scraping function ---
def fetch_page_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text(separator=' ')
    except Exception as e:
        return f"Error fetching page: {e}"

# --- Langchain LLM extraction ---

def extract_car_info_with_groq(text_content):
    llm = ChatGroq(model_name="Gemma2-9b-It", temperature=0)


    # Prompt template for extracting car information
    prompt = ChatPromptTemplate.from_template("""
You are part of a backend system and must respond ONLY with valid JSON and all the values must be strictly a number.
From the car page content, extract:
- original_price(on-road price) (₹)
- company_claimed_mileage (km/l)
- engine (CC)
- max_power (bhp or kW)

Output *only* valid JSON:
{{
  "original_price": "...",
  "company_claimed_mileage": "...",
  "engine": "...",
  "max_power": "..."
}}

Do not explain anything. No other text.

Page Content:
{text}
""")

    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.invoke({"text": text_content[:5000]})

    response_text = result.get("text", "").strip()

    # ✅ Catch parse error and return safely
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("❌ JSONDecodeError: ", repr(response_text))  # Log exact error
        return {
            "error": "Invalid JSON from LLM",
            "raw_response": response_text
        }


# --- Core Logic ---
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

# --- API Schema ---
class CarQuery(BaseModel):
    car_name: str
    model: str
    year: str
    fuel_type: str
    variant: str

# --- Endpoint ---
@app.post("/get-car-info")
def get_car_info(query: CarQuery):
    result = get_car_info_online(
        query.car_name,
        query.model,
        query.year,
        query.fuel_type,
        query.variant
    )

    # ✅ Return structured error or parsed result
    if isinstance(result, dict) and "error" in result:
        return result
    
    else:
        print(result)
        return {"result": result}
        
    
