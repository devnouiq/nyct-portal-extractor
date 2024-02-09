import requests
import argparse
import psycopg2
import time  # Importing time for sleep
from data_extraction import get_soup, retrieve_all_data, update_data
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL="https://nyctportal.global-terminal.com/gctusa/gctces/index.php"

DB_CONFIG = {
   "dbname": "nyct_portl",
   "user": "nyct_user",
   "password": "Apple@123",
   "host": "localhost",
   "port": "5432",
}

URL_TEMPLATE = f"{BASE_URL}?pageId=37&q=*&start={{}}&count=19"

def get_cookies():
    try:
        with open("cookie.json", "r") as file:
            cookies = json.load(file)
            return cookies
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")

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


def run_single_request(url, cursor, sleep_interval,conn, args):
    time.sleep(sleep_interval)  # Sleep for the specified interval
    soup = get_soup(url, get_headers(get_cookies()))
    if soup and args.operation_type != "update":
        retrieve_all_data(soup, cursor)
    else:
        update_data(soup, cursor)
    conn.commit()

def fetch_and_process_data(args, cursor, last_carrier_id,conn):
    sleep_interval = int(args.sleep) if args.sleep else 10  # Default sleep interval is 10 seconds
    num_requests = int(args.count) if args.count else 1  # Default to 1 request if count is not specified

    if args.operation_type == "new":
        if args.name:
            url = f"{BASE_URL}?pageId=61&tabId=&scac={args.name}"
            logger.info(f"Running for carrier: {args.name}")
            run_single_request(url, cursor, sleep_interval, conn, args)
        else:
            start_value = last_carrier_id
            for _ in range(num_requests):
                list_url = URL_TEMPLATE.format(start_value)

                res = requests.get(list_url, headers=get_headers(get_cookies()))
                data = res.json()

                for item in data.get("items", []):
                    name = item.get("name")
                    url = f"{BASE_URL}?pageId=61&tabId=&scac={name}"
                    logger.info(f"Running for carrier: {name}")
                    run_single_request(url, cursor, sleep_interval,conn, args)

                start_value += 20
    elif args.operation_type == "update" and args.name:
        logger.info(f"Updating data for specific carrier: {args.name}")
        url = f"{BASE_URL}?pageId=61&tabId=&scac={args.name}"
        run_single_request(url, cursor, sleep_interval, conn, args)
        


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--name', help='Specify a carrier name for the URL')
    parser.add_argument('--count', type=int, help='Specify number of requests to scrape',default=10)
    parser.add_argument('--sleep', type=int, help='Specify the sleep interval in seconds',default=1)
    parser.add_argument('--operation_type', help='Specify the operation type',default='new', choices=['new', 'update'])

    args = parser.parse_args()

    if args.operation_type == 'update' and not args.name:
        parser.error("If operation type is 'update', you must specify a carrier name with --name.")

    with connect_to_database() as conn:
        with conn.cursor() as cursor:
            if table_exists(cursor, "carrier_info"):
                cursor.execute("SELECT carrier_id FROM carrier_info ORDER BY carrier_id DESC LIMIT 1;")
                last_carrier_id = cursor.fetchone()[0] if cursor.rowcount else 0
            else:
                last_carrier_id = 0

            fetch_and_process_data(args, cursor, last_carrier_id,conn)
            

if __name__ == "__main__":
    main()