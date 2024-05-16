from .util.site_api_handler import SiteApiInterface
from dotenv import load_dotenv
import os

url = "https://weatherapi-com.p.rapidapi.com/current.json"

load_dotenv()
headers = {
    "X-RapidAPI-Key": os.getenv("WEATHER_API_KEY"),
    "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
}

site_api = SiteApiInterface()

if __name__ == '__main__':
    site_api()
