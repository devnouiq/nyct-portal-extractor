import requests
import argparse
import logging
import psycopg2
from data_extraction import get_soup, retrieve_all_data
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": "your_database_name",
    "user": "your_database_user",
    "password": "your_database_password",
    "host": "your_database_host",
    "port": 5432
}

URL_TEMPLATE = "https://nyctportal.global-terminal.com/gctusa/gctces/index.php?pageId=37&q=*&start={}&count=20"

# example cookies
def get_cookies():
    return {
        "PHPSESSID": "9n2t51adoobk9d8e0i394mjiha5o0a8h",
        "ZDEDebuggerPresent": "php,phtml,php3",
        "publicId_gctusa_gctces": "65b881b02f5dc9.09483808",
        "settings_gctusa_gctces": "%7B%22altuser%22%3A%2265b881b02f5dc9.09483808%22%7D",
        "sidebarNav_gctusa_gctces": "%7B%22width%22%3A193%7D",
    }


def get_headers(cookies):
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.6",
        "content-type": "application/x-www-form-urlencoded",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "cookie": "; ".join([f"{name}={value}" for name, value in cookies.items()]),
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }


def table_exists(cursor, table_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM   information_schema.tables
            WHERE  table_name = %s
        );
    """, (table_name,))
    return cursor.fetchone()[0]


def connect_to_database():
    return psycopg2.connect(**DB_CONFIG)


def run_single_request(url, cursor):
    soup = get_soup(url, get_headers(get_cookies()))

    if soup:
        retrieve_all_data(soup, cursor)

def fetch_and_process_data(args, cursor, last_carrier_id):
    if args.name:
        url = f"https://nyctportal.global-terminal.com/gctusa/gctces/index.php?pageId=61&tabId=&scac={args.name}"
        logger.info(f"Running for carrier: {args.name}")
        run_single_request(url, cursor)
    else:
        num_requests = 1

        for _ in range(num_requests):
            start_value = last_carrier_id
            list_url = URL_TEMPLATE.format(start_value)

            res = requests.get(list_url, headers=get_headers(get_cookies()))
            data = res.json()

            for item in data.get("items", []):
                name = item.get("name")
                url = f"https://nyctportal.global-terminal.com/gctusa/gctces/index.php?pageId=61&tabId=&scac={name}"
                logger.info(f"Running for carrier: {name}")
                run_single_request(url, cursor)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--name', help='Specify a carrier name for the URL')
    args = parser.parse_args()

    with connect_to_database() as conn:
        with conn.cursor() as cursor:
            if table_exists(cursor, "carrier_info"):
                cursor.execute("SELECT carrier_id FROM carrier_info ORDER BY carrier_id DESC LIMIT 1;")
                last_carrier_id = cursor.fetchone()[0] if cursor.rowcount else 0
            else:
                last_carrier_id = 0

            fetch_and_process_data(args, cursor, last_carrier_id)

if __name__ == "__main__":
    main()
