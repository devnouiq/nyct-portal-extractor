import requests
import logging
from bs4 import BeautifulSoup
import re
from db_connections import (
    create_carrier_info_table,
    create_drivers_table,
    create_line_auth_table,
    create_notes_table,
    insert_data_into_carrier_info_table,
    insert_data_into_drivers_table,
    insert_data_into_line_auth_table,
    insert_notes_data
)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_soup(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        logger.error(f"Error: {response.status_code}")
        return None

def extract_carrier_info(soup):
    carrier_info = {}
    carrier_row = soup.find('td', class_='edit_data', colspan='3')
    if carrier_row:
        carrier_text = carrier_row.get_text(strip=True)
        carrier_info['Carrier'] = carrier_text.replace('\xa0','').split(':')[0].strip()
        carrier_info['Carrier Name'] = (carrier_text.replace('\xa0', '').split(':', 1) + [''])[1].strip()
    
    other_rows = soup.find_all('tr')

    for row in other_rows:
        labels = row.find_all('td', class_='edit_label')
        data_entries = row.find_all('td', class_='edit_data')

        for label, data in zip(labels, data_entries):
            label_text = label.get_text(strip=True).replace('\xa0', ' ')
            data_text = data.get_text(strip=True).replace('\xa0', ' ')
            if label_text != 'Address':
                carrier_info[label_text] = data_text
        
        for i in range(len(data_entries)-1):
            label_text = labels[i].get_text(strip=True).replace('\xa0', ' ')
            if label_text == 'Address':
                address_txt = data_entries[i].get_text(strip=True).replace('\xa0', ' ')
                address_txt += " " + data_entries[i+1].get_text(strip=True).replace('\xa0', ' ')
                if data_entries[i+2] is not None and 'colspan' in data_entries[i+2].attrs:
                    address_txt += " " + data_entries[i+2].get_text(strip=True).replace('\xa0', ' ')
                carrier_info['Address'] = address_txt
                break

        checkbox_input = row.find('input', {'type': 'checkbox'})
        value = 'true' if checkbox_input and 'checked' in checkbox_input.attrs else 'false'
        
        checkbox_label = row.find('label')
        
        if checkbox_label:
            checkbox_label_text = checkbox_label.get_text(strip=True).replace('\xa0', ' ')
            carrier_info[checkbox_label_text] = value

    terminal_auth_str = carrier_info.get('Terminal Auth', '').lower()
    terminal_auth = True if terminal_auth_str == 'true' else False
    
    data = (
        carrier_info.get('Carrier', '').split(':')[0].strip(),
        carrier_info.get('Carrier Name', ''),
        carrier_info.get('Status', ''),
        carrier_info.get('Effective', ''),
        carrier_info.get('Address', ''),
        carrier_info.get('Telephone', ''),
        carrier_info.get('FAX', ''),
        carrier_info.get('Email Address', ''),
        re.sub(r'\s{2,}', ' ',carrier_info.get('Contact Person', '')),
        terminal_auth
    )
    return data

def extract_driver_info(soup):
    drivers = {}
    div_element = soup.find('div', id='tabDrivers')
    table_data_rows = div_element.find_all('tr', class_='table_data_rowhover')
    for i, row in enumerate(table_data_rows, start=1):
        data_elements = row.find_all('td', class_='table_data')
        if len(data_elements) >= 7:
            sea_link = data_elements[0].get_text(strip=True)
            input_element = data_elements[1].find('input')
            auth = 'true' if input_element and 'checked' in input_element.attrs else 'false'
            name = data_elements[2].get_text(strip=True)
            status = data_elements[3].get_text(strip=True)
            status_date = data_elements[4].get_text(strip=True)
            relationship = data_elements[5].get_text(strip=True)
            relationship_date = data_elements[6].get_text(strip=True)

            drivers[i] = {
                'SeaLink': sea_link,
                'Auth': auth,
                'Name': name,
                'Status': f'{status} {status_date}',
                'Relationship': f'{relationship} {relationship_date}'
            }

    return drivers

def extract_line_auth_info(soup):
    line_auth = {}
    div_element = soup.find('div', id='tabLineAuths')
    table_data_rows = div_element.find_all('tr', class_='table_data_rowhover')

    for i, row in enumerate(table_data_rows, start=1):
        data_elements = row.find_all('td', class_='table_data')
        input_element = data_elements[1].find('input')
        value = 'true' if input_element and 'checked' in input_element.attrs else 'false'

        line_auth[i] = [data_elements[0].get_text(strip=True), value, data_elements[2].get_text(strip=True)]

    return line_auth

def extract_notes(soup):
    notes = ""
    div_element = soup.find('div', id='tabNotes')
    span_elements = div_element.find_all('span')
    for span in span_elements:
        note_text = span.get_text(strip=True).replace('\xa0', ' ')
        notes += note_text

    return notes

def retrieve_all_data(soup, cursor):
    carrier_info = extract_carrier_info(soup)
    create_carrier_info_table(cursor)
    carrier_name = carrier_info[0]
    insert_data_into_carrier_info_table(cursor, carrier_info)
    logger.info("Data has been inserted into the 'carrier_info' table.")
    
    drivers = extract_driver_info(soup)
    create_drivers_table(cursor)
    insert_data_into_drivers_table(cursor, drivers, carrier_name)
    logger.info("Data has been inserted into the 'drivers' table.")

    line_auth = extract_line_auth_info(soup)
    create_line_auth_table(cursor)
    insert_data_into_line_auth_table(cursor, line_auth, carrier_name)
    logger.info("Data has been inserted into the 'line_Auth' table.")

    notes = extract_notes(soup)
    create_notes_table(cursor)
    insert_notes_data(cursor, notes, carrier_name)
    logger.info("Data has been inserted into the 'notes' table.")

def update_data(soup, cursor):
    carrier_info = extract_carrier_info(soup)
    carrier_name = carrier_info[0]
    insert_data_into_carrier_info_table(cursor, carrier_info)
    logger.info("Data has been updated into the 'carrier_info' table.")

    drivers = extract_driver_info(soup)
    insert_data_into_drivers_table(cursor, drivers, carrier_name)
    logger.info("Data has been updated into the 'drivers' table.")
    
    line_auth = extract_line_auth_info(soup)
    insert_data_into_line_auth_table(cursor, line_auth, carrier_name)
    logger.info("Data has been updated into the 'line_Auth' table.")
    
    notes = extract_notes(soup)
    insert_notes_data(cursor, notes, carrier_name)
    logger.info("Data has been updated into the 'notes' table.")