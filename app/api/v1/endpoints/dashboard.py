from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/weather")
async def get_weather(lat: float = 23.0225, lon: float = 72.5714): # Defaults to Ahmedabad
    # In production, this would call OpenWeatherMap API
    return {
        "location": "Central Hub",
        "temperature": 28,
        "condition": "Partly Cloudy",
        "humidity": 45,
        "wind_speed": 12,
        "forecast": [
            {"day": "Tue", "temp": 29, "condition": "Sunny"},
            {"day": "Wed", "temp": 27, "condition": "Rain"},
            {"day": "Thu", "temp": 30, "condition": "Clear"}
        ]
    }

@router.get("/market")
async def get_market_prices():
    # In production, this would fetch from Agmarknet or similar
    return [
        {"crop": "Wheat (High Quality)", "price": 2450, "unit": "Quintal", "change": +2.5, "mandi": "Ahmedabad"},
        {"crop": "Paddy (Basmati)", "price": 4200, "unit": "Quintal", "change": -1.2, "mandi": "Patiala"},
        {"crop": "Citrus (Grade A)", "price": 3800, "unit": "Quintal", "change": +5.0, "mandi": "Nagpur"},
        {"crop": "Cotton", "price": 7100, "unit": "Quintal", "change": 0.0, "mandi": "Amravati"}
    ]

@router.get("/news")
async def get_agri_news():
    return [
        {
            "id": 1,
            "title": "New Government Subsidy for Drip Irrigation",
            "source": "AgriDaily",
            "time": "2 hours ago"
        },
        {
            "id": 2,
            "title": "Citrus Pests Warning in Southern Districts",
            "source": "Plant Health Dept",
            "time": "5 hours ago"
        }
    ]
