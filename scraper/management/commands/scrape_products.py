from django.core.management.base import BaseCommand
from django.utils import timezone
from scraper.models import Store, Product
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class Command(BaseCommand):
    help = 'Scrape product data from supermarkets'

    def handle(self, *args, **kwargs):
        print("Starting scraper...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options, executable_path=ChromeDriverManager().install())

        headers = {
            'User-Agent': 'ProductComparisonBot/1.0 (+your.email@example.com)'
        }

        stores = [
            {'name': 'Lidl', 'url': 'https://www.lidl.ie/c/food-drink/s10068374'},
            # {'name': 'Tesco', 'url': 'https://www.tesco.ie/groceries/en-IE/shop/food-cupboard/all'},
            # {'name': 'SuperValu', 'url': 'https://shop.supervalu.ie/sm/delivery/rsid/5550/categories/food-cupboard-id-O100035'},
        ]

        for store_data in stores:
            print(f"Processing {store_data['name']} at {store_data['url']}")
            store, created = Store.objects.get_or_create(name=store_data['name'], url=store_data['url'])

            try:
                driver.get(store_data['url'])
                time.sleep(5)  # Wait for dynamic content
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                print(f"Found {len(soup.select('.product-grid-box'))} product grid boxes")  # Debug

                if store_data['name'] == 'Lidl':
                    products = soup.select('.product-grid-box')  # Container for each product
                    print(f"Found {len(products)} products for Lidl")
                    for item in products:
                        # Extract product name
                        name_element = item.select_one('.product-grid-box__title')
                        name = name_element.text.strip() if name_element else 'Unknown'
                        print(f"Extracted name: {name}")

                        # Extract price
                        price_element = item.select_one('.ods-price__value')
                        price_text = price_element.text.strip() if price_element else '0.0'
                        price = float(price_text.replace('€', '').replace(',', '')) if price_text else 0.0
                        print(f"Extracted price: {price}€")

                        # Extract prefix (e.g., 'each', 'per kg')
                        prefix_element = item.select_one('.ods-price__prefix')
                        weight = prefix_element.text.strip() if prefix_element else ''
                        print(f"Extracted prefix/weight: {weight}")

                        # Save to database
                        Product.objects.create(
                            name=name,
                            weight=weight,  # Using prefix as weight for now
                            price=price,
                            store=store,
                            category='Food & Drink',
                            scraped_date=timezone.now()
                        )
                        print(f"Saved: {name}, {weight}, {price}€")

                    self.stdout.write(self.style.SUCCESS(f'Successfully scraped {store_data["name"]}'))

            except Exception as e:
                print(f"Error scraping {store_data['name']}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'Error scraping {store_data["name"]}: {str(e)}'))

        driver.quit()
        print("Scraper finished.")