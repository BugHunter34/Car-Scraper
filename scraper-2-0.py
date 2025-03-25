# Import necessary libraries
import requests
from bs4 import BeautifulSoup
from pypac import PACSession, get_pac
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load PAC file and create PACSession
pac = get_pac(url='http://127.0.0.1:9001/localproxy-2816cff9.pac')
session = PACSession(pac)

# List of predefined brands
brands = ["Alfa Romeo","Land Rover","Škoda" ,"Audi", "Ford", "Opel", "Toyota", "BMW", "Hyundai", "Peugeot", "Volkswagen", "Citroën","Dacia", "Mazda", "Renault", "Volvo", "Fiat", "Mercedes-Benz", "Tesla"]

def detect_brand(car_name):
    for brand in brands:
        if brand.lower() in car_name.lower():
            return brand
    return "Unknown"

def scrap_price(pages_to_scrape):
    cars = []
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

        # Find all car elements within the list and take the first 6
        car_elements = car_list.find_all('li', class_='c-item')[:6]
        
        for element in car_elements:
            car_container = element.find('div', class_='c-item__container')
            car_content = car_container.find('div', class_='c-item__content')
            car_data_wrap = car_content.find('div', class_='c-item__data-wrap')
            
            car_link = car_data_wrap.find('a', class_='c-item__link')
            car_name_element = car_link.find('span', class_='c-item__name')
            car_model_element = car_link.find('span', class_='c-item__name--suffix')
            car_price_element = car_data_wrap.find('div', class_='c-item__data').find('div', class_='c-item__price')
            
            if car_name_element and car_model_element and car_price_element:
                car_name = car_name_element.text.strip()
                car_model = car_model_element.text.strip()
                car_price = car_price_element.text.strip()
                
                # Combine name and model
                # full_name = f"{car_name} {car_model}"
                
                # Detect brand
                brand = detect_brand(car_name)
                
                # Remove currency symbols and non-breaking spaces, convert price to integer (if possible)
                car_price = car_price.replace('Kč', '').replace('\xa0', '').replace(',', '').strip()
                try:
                    car_price = int(car_price)
                except ValueError:
                    car_price = 'N/A'
                
                cars.append({'brand': brand, 'name': car_name,'price': car_price, 'model': car_model})
            else:
                print(f"Error: Missing car name, model, or price element on page {page}.")
    
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
                file.write(f"- Name: {car['name']}, Price: {car['price']} Kč, Detail: {car['model']}\n")
            file.write("\n")

# Number of pages to scrape
pages_to_scrape = 20

sorted_car_list = scrap_price(pages_to_scrape)

# Save the sorted list to a file
save_to_file(sorted_car_list, 'sorted_cars.txt')

print("The sorted car list has been saved to sorted_cars.txt.")
