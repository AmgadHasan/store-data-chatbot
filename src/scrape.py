import re
import sqlite3
import time
from typing import Dict, List, Union

import requests
from bs4 import BeautifulSoup

from src.utils import create_logger

logger = create_logger(logger_name="scraper")


def get_total_pages_and_products(base_url: str) -> tuple[int, int]:
    """
    Dynamically determine the total number of pages and products from the home page.

    Args:
        base_url (str): The URL of the home page.

    Returns:
        tuple[int, int]: A tuple containing the total number of pages and total number of products.
    """
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find results summary text
    form = soup.find("form", class_="form-horizontal")
    results_text = form.get_text(strip=True) if form else ""

    # Extract total products
    match = re.search(r"(\d+)\s*results", results_text)
    total_products = int(match.group(1)) if match else 0

    # Find page summary text
    page_text_elem = soup.find("li", class_="current")
    page_text = page_text_elem.text.strip() if page_text_elem else ""

    # Extract total pages
    match = re.search(r"Page \d+ of (\d+)", page_text)
    total_pages = int(match.group(1)) if match else 0

    return total_pages, total_products


def scrape_book_details(book_url: str) -> tuple[str, str, int]:
    """
    Scrape detailed information for a specific book.

    Args:
        book_url (str): The URL of the book's detail page.

    Returns:
        tuple[str, str, int]: A tuple containing the book's description, category, and stock quantity.
    """
    response = requests.get(book_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract description
    description_elem = soup.find("div", id="product_description")
    description = (
        description_elem.find_next("p").text if description_elem else "No description"
    )

    # Extract category
    breadcrumb = soup.find("ul", class_="breadcrumb")
    category = (
        breadcrumb.find_all("a")[2].text
        if breadcrumb and len(breadcrumb.find_all("a")) > 2
        else "Unknown"
    )

    # Extract stock quantity
    availability_elem = soup.find("p", class_="instock availability")
    stock_text = availability_elem.text.strip() if availability_elem else ""
    match = re.search(r"In stock \((\d+) available\)", stock_text)
    stock_quantity = int(match.group(1)) if match else 0

    return description, category, stock_quantity


def scrape_book_page(url: str) -> List[Dict[str, Union[str, float, int]]]:
    """
    Scrape details for books on a single page.

    Args:
        url (str): The URL of the page to scrape.

    Returns:
        list[dict[str, str | float | int]]: A list of dictionaries containing book details.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    books = []
    book_elements = soup.find_all("article", class_="product_pod")

    for book in book_elements:
        # Basic book information
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text[1:]  # Remove £ symbol

        # Get star rating
        star_class = book.find("p", class_="star-rating")["class"][1]
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        star_rating = rating_map.get(star_class, 0)

        # Get availability
        availability = book.find("p", class_="instock availability").text.strip()

        # Get book page URL to scrape more details
        book_page_url = "https://books.toscrape.com/catalogue/" + book.h3.a[
            "href"
        ].replace("../", "")

        # Scrape additional details
        description, category, quantity = scrape_book_details(book_page_url)

        books.append(
            {
                "title": title,
                "price": float(price),
                "star_rating": star_rating,
                "availability": availability,
                "description": description,
                "category": category,
                "quantity": quantity,
            }
        )

    return books


def scrape_all_books(
    base_url: str, page_url_template: str
) -> List[Dict[str, Union[str, float, int]]]:
    """
    Scrape books from all pages.

    Args:
        base_url (str): The base URL of the website.
        page_url_template (str): The URL template for pagination.

    Returns:
        list[dict[str, str | float | int]]: A list of dictionaries containing all scraped book details.
    """
    total_pages, total_products = get_total_pages_and_products(base_url)

    logger.info(f"Total Products: {total_products}")
    logger.info(f"Total Pages: {total_pages}")

    all_books = []

    for page_num in range(1, total_pages + 1):
        url = page_url_template.format(page_num)
        logger.info(f"Scraping page {page_num}")

        try:
            page_books = scrape_book_page(url)
            all_books.extend(page_books)
            time.sleep(0.1)  # Polite scraping: add a delay between requests
        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")

    return all_books


def save_to_sqlite(data: List[Dict[str, Union[str, float, int]]], db_path: str) -> None:
    """
    Save the scraped data to an SQLite database.

    Args:
        data (list[dict[str, str | float | int]]): The data to save.
        db_path (str): The path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            star_rating INTEGER NOT NULL,
            availability TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    # ```sql\nCREATE TABLE products (\n\tmain_category TEXT, \n\ttitle TEXT, \n\taverage_rating FLOAT, \n\trating_number BIGINT, \n\tfeatures TEXT, \n\tdescription TEXT, \n\tprice TEXT, \n\tstore TEXT, \n\tcategories TEXT, \n\tdetails TEXT, \n\tparent_asin TEXT\n)```

    # Insert data
    for book in data:
        cursor.execute(
            """
            INSERT INTO books (title, price, star_rating, availability, description, category, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                book["title"],
                book["price"],
                book["star_rating"],
                book["availability"],
                book["description"],
                book["category"],
                book["quantity"],
            ),
        )

    conn.commit()
    conn.close()
    logger.info(f"Data saved to {db_path}")


def main() -> None:
    logger.info("Scraping data")
    base_url = "https://books.toscrape.com/index.html"
    page_url_template = "https://books.toscrape.com/catalogue/page-{0}.html"

    books_data = scrape_all_books(base_url, page_url_template)

    save_to_sqlite(books_data, "data/books_data.db")

    logger.info(f"Scraped {len(books_data)} books. Data saved to books.db")


if __name__ == "__main__":
    main()
