from django.core.management.base import BaseCommand
from django.utils import timezone
from scraper.models import Store, Product
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class Command(BaseCommand):
    help = 'Scrape product data from supermarkets'

    def handle(self, *args, **kwargs):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        stores = [
            {'name': 'Lidl', 'url': 'https://www.lidl.ie/c/food-drink'},
            {'name': 'Tesco', 'url': 'https://www.tesco.ie/groceries/en-IE/shop/food-cupboard/all'},
            {'name': 'SuperValu', 'url': 'https://shop.supervalu.ie/sm/delivery/rsid/5550/categories/food-cupboard-id-O100035'},
        ]

        for store_data in stores:
            store, created = Store.objects.get_or_create(name=store_data['name'], url=store_data['url'])

            try:
                driver.get(store_data['url'])
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                if store_data['name'] == 'Lidl':
                    products = soup.select('.product-grid__item')  # Update selector
                    for item in products:
                        name = item.select_one('.product__title').text.strip() if item.select_one('.product__title') else 'Unknown'
                        weight = item.select_one('.product__weight').text.strip() if item.select_one('.product__weight') else ''
                        price_text = item.select_one('.price__value').text.strip() if item.select_one('.price__value') else '0.0'
                        price = float(price_text.replace('€', '').replace(',', ''))
                        Product.objects.create(
                            name=name,
                            weight=weight,
                            price=price,
                            store=store,
                            category='Food & Drink',
                            scraped_date=timezone.now()
                        )
                elif store_data['name'] == 'Tesco':
                    products = soup.select('.product-list--list-item')  # Update selector
                    for item in products:
                        name = item.select_one('.product-tile__title').text.strip() if item.select_one('.product-tile__title') else 'Unknown'
                        weight = item.select_one('.product-tile__weight').text.strip() if item.select_one('.product-tile__weight') else ''
                        price_text = item.select_one('.price-per-unit').text.strip() if item.select_one('.price-per-unit') else '0.0'
                        price = float(price_text.replace('€', '').replace(',', ''))
                        Product.objects.create(
                            name=name,
                            weight=weight,
                            price=price,
                            store=store,
                            category='Food Cupboard',
                            scraped_date=timezone.now()
                        )
                elif store_data['name'] == 'SuperValu':
                    products = soup.select('.product-list-item')  # Update selector
                    for item in products:
                        name = item.select_one('.product-name').text.strip() if item.select_one('.product-name') else 'Unknown'
                        weight = item.select_one('.product-weight').text.strip() if item.select_one('.product-weight') else ''
                        price_text = item.select_one('.product-price').text.strip() if item.select_one('.product-price') else '0.0'
                        price = float(price_text.replace('€', '').replace(',', ''))
                        Product.objects.create(
                            name=name,
                            weight=weight,
                            price=price,
                            store=store,
                            category='Food Cupboard',
                            scraped_date=timezone.now()
                        )

                self.stdout.write(self.style.SUCCESS(f'Successfully scraped {store_data["name"]}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error scraping {store_data["name"]}: {str(e)}'))

        driver.quit()