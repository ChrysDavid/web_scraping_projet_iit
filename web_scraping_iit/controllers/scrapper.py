import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from .file_manager import FolderManager, FileManager

class BookScraper:
    def __init__(self, url, category=''):
        self.url = url
        self.category = category
        self.int_scraper()

    def int_scraper(self):
        r = requests.get(self.url)
        self.bs4_parser(r)

    def bs4_parser(self, r):
        book_data = BeautifulSoup(r.text, 'html.parser')
        search_values = self.search(book_data)
        self.get_book_url(search_values)

    def search(self, book_data):
        return book_data.find_all('article', {'class': 'product_pod'})

    def get_book_url(self, datas):
        book_urls = [c.find("a")["href"].strip() for c in datas]
        self.get_book_data(book_urls)

    def get_book_data(self, book_urls):
        for url in book_urls:
            book_url = urljoin(self.url, url)
            with requests.get(book_url) as response:
                if response.status_code == 200:
                    book_soup = BeautifulSoup(response.text, 'html.parser')
                    # Extraction des informations du livre
                    book_name = book_soup.select_one("h1").text
                    book_price = book_soup.select_one("p.price_color").text
                    book_rating = book_soup.select_one("p.star-rating")["class"][1]
                    book_description = book_soup.select_one("meta[name=description]")["content"]
                    availability = book_soup.select_one("p.availability").text.strip()
                    img_urls = [img["src"] for img in book_soup.select("div.image_container img")]

                    FolderManager(self.category)
                    file_manager = FileManager(self.category)
                    
                    for img_url in img_urls:
                        # Ajout des informations au fichier Excel (chaque URL d'image dans une cellule différente)
                        book_info = [book_name, book_price, book_rating, book_description, availability, img_url]
                        file_manager.write_to_excel(book_info)

                        # Téléchargement et enregistrement de l'image dans le dossier "images" avec le nom du livre
                        images_folder = os.path.join('datas', self.category, 'images')
                        download_image(img_url, images_folder, book_name)



def download_image(url, folder_path, book_name):
    if not url.startswith("http"):
        url = urljoin("https://books.toscrape.com", url)

    response = requests.get(url)
    if response.status_code == 200:
        image_filename = f"{book_name}.jpg"
        image_path = os.path.join(folder_path, image_filename)
        with open(image_path, 'wb') as file:
            file.write(response.content)


class CategoryScraper:
    def __init__(self, url, BASE_URL=''):
        self.url = url
        self.BASE_URL = BASE_URL
        self.int_scraper()

    def int_scraper(self):
        with requests.get(self.url) as r:
            self.bs4_parser(r)

    def bs4_parser(self, r):
        cat_data = BeautifulSoup(r.text, 'html.parser')
        search_values = self.search_cat_and_url(cat_data)
        self.get_all_cat_book_data(search_values)

    def search_cat_and_url(self, cat_data):
        cat_div = cat_data.select("ul.nav-list > li > ul > li > a")

        if cat_div:
            for a in cat_div:
                all_cat_url = urljoin(self.BASE_URL, a.get("href").strip())
                FolderManager(a.get_text().strip())
                BookScraper(all_cat_url, a.get_text().strip())

    def get_all_cat_book_data(self, urls):
        pass
