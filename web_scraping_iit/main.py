from controllers import scrapper

def main():
    url = "https://books.toscrape.com/index.html"
    BASE_URL = "https://books.toscrape.com/index.html"

    scrapper.CategoryScraper(url, BASE_URL)



if __name__ == '__main__':
    main()


