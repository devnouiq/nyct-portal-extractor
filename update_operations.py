import psycopg2
from db_connections import (
    update_data_in_carrier_info_table,
    update_notes_data,
    update_data_in_drivers_table,
    update_data_in_line_auth_table
)

DB_CONFIG = {
    "dbname": "your_database_name",
    "user": "your_database_user",
    "password": "your_database_password",
    "host": "your_database_host",
    "port": 5432
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    carrier_id_to_update = 1
    new_data = ('New Carrier', 'New Status', 'New Address', 'New Telephone', 'New Email', 'New Contact Person')
    update_data_in_carrier_info_table(cursor, carrier_id_to_update, new_data)

    driver_id_to_update = 1
    new_driver_data = {
        'SeaLink': 'New SeaLink',
        'Auth': 'true',
        'Name': 'New Driver Name',
        'Status': 'New Status',
        'Relationship': 'New Relationship'
    }
    update_data_in_drivers_table(cursor, driver_id_to_update, [new_driver_data[key] for key in ['SeaLink', 'Auth', 'Name', 'Status', 'Relationship']])

    line_auth_id_to_update = 1
    new_line_auth_data = {
        'Line': 'New Line',
        'Auth': 'true',
        'LineCarrier': 'New Line Carrier'
    }
    update_data_in_line_auth_table(cursor, line_auth_id_to_update, [new_line_auth_data[key] for key in ['Line', 'Auth', 'LineCarrier']])

    note_id_to_update = 1
    new_notes_data = 'New notes content'
    update_notes_data(cursor, note_id_to_update, new_notes_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
