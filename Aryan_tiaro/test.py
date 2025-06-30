import requests

payload = {
    "car_name": "Maruti",
    "model": "Dzire",
    "year": "2022",
    "fuel_type": "petrol",
    "variant": "ZXI"
}

res = requests.post("http://127.0.0.1:8000/get-car-info", json=payload)
print(res.json())
