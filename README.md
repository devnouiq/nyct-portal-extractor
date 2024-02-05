# Web Scraping and Data Extraction Readme

## Overview

This script is designed to scrape data from a specific website and store it in a PostgreSQL database. It uses the `requests` library to make HTTP requests, `BeautifulSoup` for web scraping, and `psycopg2` for connecting to and interacting with a PostgreSQL database. The extracted data is then processed using functions from the `data_extraction` module.

## Installation

1. Install the required Python libraries:

   ```bash
   pip3 install virtualenv
   virtualenv env
   source venv/bin/activate
   sudo apt-get install --reinstall libpq-dev
   pip install requests
   pip install beautifulsoup4
   pip install psycopg2
   pip install argparse
   ```

### PostgreSQL Installation

1. Download the PostgreSQL installer for Windows from the official website: [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

2. Run the installer and follow the on-screen instructions to install PostgreSQL. During the installation, take note of the following:

   - PostgreSQL Database Superuser: **your_postgres_user**
   - PostgreSQL Database Password: **your_postgres_password**
   - PostgreSQL Port: **5432** (default)

3. Complete the installation process.

### Database Configuration

1. Open a command prompt and navigate to the PostgreSQL `bin` directory. This is typically located in the PostgreSQL installation directory. For example:

   ```bash
   cd C:\Program Files\PostgreSQL\your_postgres_version\bin
   ```

2. Initialize a new PostgreSQL database. Replace **your_database_name** with the desired name for your database:

   ```bash
   createdb -U your_postgres_user -O your_postgres_user -h localhost -p 5432 your_database_name
   ```

   Enter the PostgreSQL password when prompted.

### Update `DB_CONFIG` in the Script

1. Open the `script.py` file in a text editor.

2. Locate the `DB_CONFIG` dictionary and update it with the PostgreSQL configuration:

   ```python
   DB_CONFIG = {
      "dbname": "your_database_name",
      "user": "your_postgres_user",
      "password": "your_postgres_password",
      "host": "localhost",
      "port": "5432",
   }
   ```

## DB Schema

![db_Schema](./images/image.png)

## Steps for Authentication

1. **Open Developer Console:**
   - After logging in, navigate to the website.
   - Open the browser's developer console using `Ctrl+Shift+I`.

2. **Run the Following Command:**
   - Once the console is open, paste and run the following JavaScript command:

   ```javascript
   cookieStore.getAll().then(cookies => {
      const combinedCookies = {};

      cookies.forEach(cookie => {
         const { name, value } = cookie;
         combinedCookies[name] = value;
      });

      const jsonCookies = JSON.stringify(combinedCookies, null, 2);
      console.log(jsonCookies);
   });
   ```

3. **Copy JSON Output:**
   - After running the command, the console will display a JSON representation of the cookies.

4. **Save to `cookie.json` File:**
   - Copy the entire JSON output.
   - Create or open the `cookie.json` file.
   - Paste the copied JSON into the `cookie.json` file and save it.

   Example :
   ![cookies](./images/image-1.png)

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/nyct-portal-extractor.git
   ```

2. Navigate to the project directory:

   ```bash
   cd nyct-portal-extractor
   ```

3. Run the script with the following command:

   ```bash
   python script.py [--name NAME]
   ```

   or 

   ```bash
   python script.py
   ```

   ### Note:
      The optional `--name` argument allows you to specify a carrier name for which you want to extract data. If not provided, the script will run for all carriers.

   Adjust the following parameters in the script according to your requirements:

   ```python
   num_requests = 1  # Set the number of requests to be sent
   ```

   This script is designed to handle pagination automatically. It sends requests to the specified URL template with different start values to retrieve sets of data.

   ```python
   url_template = "https://nyctportal.global-terminal.com/gctusa/gctces/index.php?pageId=37&q=*&start={}&count=20"
   ```

   Modify the `headers` dictionary as needed for your specific web scraping requirements.

## Data Extraction

The main data extraction function is `retrieve_all_data()`. Customize this function in the `data_extraction` module according to the structure of the data you are scraping from the website.

```python
retrieve_all_data(soup, conn, cursor)
```

## Update Operations

To update the data in the database, checkout the `update_operations` script. You can change and update specific data using the ID of specific tables. Customize the update operations according to your needs.

To run this script:

   ```bash
   python update_operations.py
   ```

## Logging

Logging is configured to display information messages. You can modify the logging level in the script based on your preferences.

   ```python
   logging.basicConfig(level=logging.INFO)
   ```
