import requests
from bs4 import BeautifulSoup
import re
from pypac import PACSession, get_pac
import urllib3
import hashlib
import time
import json

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load PAC file and create PACSession
pac = get_pac(url='http://127.0.0.1:9001/localproxy-2816cff9.pac')
session = PACSession(pac)

# List of predefined brands
brands = ["Alfa Romeo", "Kia", "Lexus", "Porsche","Jeep","MG","Suzuki", "Nissan","Subaru","Polestar", "Aston", "Dodge", "Jaguar", "Seat", "Cupra", "Land Rover", "Škoda", "Mitsubishi", "Mini", "Honda", "Lancia", "SsangYong", "Audi", "Ford", "Opel", "Toyota", "BMW", "Hyundai", "Peugeot", "Volkswagen", "Citroën", "Dacia", "Mazda", "Renault", "Volvo", "Fiat", "Mercedes-Benz", "Tesla"]

def detect_brand(car_name):
    for brand in brands:
        if brand.lower() in car_name.lower():
            return brand
    return "Unknown"

def generate_unique_id(name, kilometers, price):
    hash_input = f"{name}{kilometers}{price}".encode('utf-8')
    return hashlib.md5(hash_input).hexdigest()

def scrap_price(pages_to_scrape, existing_cars):
    cars = existing_cars.copy()
    for page in range(1, pages_to_scrape + 1):
        url = f"https://www.sauto.cz/inzerce/osobni/?strana={page}"
        # Make the request using the PACSession with SSL verification disabled
        response = session.get(url, verify=False)
        if response.status_code != 200:
            print(f"Error: Failed to retrieve page {page}. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find the list containing car elements
        car_list = soup.find('ul', class_='c-item-list__list')
        if not car_list:
            print(f"Error: No car list found on page {page}.")
            continue

        # Find all car elements within the list and take the first 17
        car_elements = car_list.find_all('li', class_='c-item')[:17]
        
        for element in car_elements:
            car_container = element.find('div', class_='c-item__container')
            car_content = car_container.find('div', class_='c-item__content')
            car_data_wrap = car_content.find('div', class_='c-item__data-wrap')
            
            car_link = car_data_wrap.find('a', class_='c-item__link')
            car_name_element = car_link.find('span', class_='c-item__name')
            car_model_element = car_link.find('span', class_='c-item__name--suffix')
            car_price_element = car_data_wrap.find('div', class_='c-item__data').find('div', class_='c-item__price')
            car_info_element = car_data_wrap.find('div', class_='c-item__info')
            
            if car_name_element and car_model_element and car_price_element and car_info_element:
                car_full_name = car_name_element.text.strip()
                car_model = car_model_element.text.strip()
                car_price = car_price_element.text.strip()
                car_info = car_info_element.text.strip()

                # Use regex to split the name and detail based on the first comma
                match = re.match(r'^(.*?)(,.*)$', car_model)
                if match:
                    car_model = match.group(1).strip()
                    detail = match.group(2).strip()
                else:
                    car_model = car_model.strip()
                    detail = ""

                # Detect brand
                brand = detect_brand(car_full_name)
                
                # Remove currency symbols and non-breaking spaces, convert price to integer (if possible)
                car_price = car_price.replace('Kč', '').replace('\xa0', '').replace(',', '').strip()
                try:
                    car_price = int(car_price)
                except ValueError:
                    car_price = 'N/A'
                
                # Extract age and kilometers driven
                car_info_parts = car_info.split(',')
                age_of_car = car_info_parts[0].strip()
                kilometers_driven = car_info_parts[1].replace('\xa0', '').strip()

                # Extract name from model
                name_parts = car_full_name.split(',')
                car_name = name_parts[0].strip()
                if len(name_parts) > 1:
                    car_model = name_parts[1].strip()
                
                # Generate unique ID
                unique_id = generate_unique_id(car_name, kilometers_driven, car_price)
                
                # Check for duplicates
                if unique_id not in [car['id'] for car in cars]:
                    cars.append({
                        'id': unique_id,
                        'brand': brand,
                        'name': car_name,
                        'detail': car_model,
                        'price': car_price,
                        'age': age_of_car,
                        'kilometers': kilometers_driven
                    })
                else:
                    print(f"Duplicate car detected: {car_name}, skipping.")
            else:
                print(f"Error: Missing car name, model, price, or info element on page {page}.")
        
        # Add a delay between requests to avoid rate limiting
        #time.sleep(1)
    
    return cars

def save_to_file(sorted_car_list, filename):
    # Group cars by brand
    grouped_cars = {}
    for car in sorted_car_list:
        if car['brand'] not in grouped_cars:
            grouped_cars[car['brand']] = []
        grouped_cars[car['brand']] = sorted(grouped_cars[car['brand']] + [car], key=lambda x: x['price'] if x['price'] != 'N/A' else float('inf'))
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as file:
        for brand in grouped_cars:
            file.write(f"Brand: {brand}\n")
            for car in grouped_cars[brand]:
                file.write(f"- ID: {car['id']}, Name: {car['name']}, Price: {car['price']} Kč, KM Driven: {car['kilometers']}, Year: {car['age']}\n")
            file.write("\n")

def load_existing_cars(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_cars_to_json(cars, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(cars, file, ensure_ascii=False, indent=4)

# Number of pages to scrape, 500 is MAX
pages_to_scrape = 500
json_filename = 'scraped_cars.json'

# Load existing cars from JSON file
existing_cars = load_existing_cars(json_filename)

# Scrape new cars and merge with existing cars
scraped_cars = scrap_price(pages_to_scrape, existing_cars)

# Save the merged car list to JSON file
save_cars_to_json(scraped_cars, json_filename)

# Save the sorted list to a text file
save_to_file(scraped_cars, 'sorted_cars.txt')

print("The sorted car list has been saved to sorted_cars.txt and scraped_cars.json.")
