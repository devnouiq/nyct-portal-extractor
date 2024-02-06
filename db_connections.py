def create_carrier_info_table(cursor):
    table_schema = '''
    CREATE TABLE IF NOT EXISTS carrier_info (
        carrier_id SERIAL,
        carrier VARCHAR(255) UNIQUE PRIMARY KEY,
        status VARCHAR(255),
        address VARCHAR(255),
        telephone VARCHAR(20),
        email_address VARCHAR(255),
        contact_person VARCHAR(255)
    );
    '''
    cursor.execute(table_schema)


def insert_data_into_carrier_info_table(cursor, data):
    insert_query = '''
    INSERT INTO carrier_info (carrier, status, address, telephone, email_address, contact_person)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (carrier) DO NOTHING;
    '''
    cursor.execute(insert_query, data)


def create_drivers_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS drivers (
            driver_id SERIAL PRIMARY KEY,
            sea_link VARCHAR(20) UNIQUE,
            auth BOOLEAN,
            name VARCHAR(255),
            status VARCHAR(255),
            relationship VARCHAR(255),
            carrier VARCHAR(255),
            FOREIGN KEY(carrier) REFERENCES carrier_info(carrier)
        );
    '''
    cursor.execute(table_schema)


def insert_data_into_drivers_table(cursor, drivers, carrier_name):
    for key, value in drivers.items():
        sea_link = value['SeaLink']
        auth = value['Auth'] == 'true'
        name = value['Name']
        status = value['Status']
        relationship = value['Relationship']

        cursor.execute("""
            INSERT INTO drivers (sea_link, auth, name, status, relationship, carrier)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sea_link) DO NOTHING;
        """, (sea_link, auth, name, status, relationship, carrier_name))


def create_line_auth_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS line_auth (
            line_auth_id SERIAL PRIMARY KEY,
            line VARCHAR(255),
            auth BOOLEAN,
            line_carrier VARCHAR(255) UNIQUE,
            carrier VARCHAR(255),
            FOREIGN KEY(carrier) REFERENCES carrier_info(carrier)
        );
    '''
    cursor.execute(table_schema)


def insert_data_into_line_auth_table(cursor, line_auth, carrier_name):
    for key, value in line_auth.items():
        line = value[0]
        auth = value[1] == 'true'
        line_carrier = value[2]
        cursor.execute("""
            INSERT INTO line_auth (line, auth, line_carrier, carrier)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (line_carrier) DO NOTHING;
        """, (line, auth, line_carrier, carrier_name))


def create_notes_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS notes (
            note_id SERIAL PRIMARY KEY,
            notes VARCHAR(255) UNIQUE,
            carrier VARCHAR(255),
            FOREIGN KEY(carrier) REFERENCES carrier_info(carrier)
        );
    '''
    cursor.execute(table_schema)


def insert_notes_data(cursor, notes, carrier_name):
    cursor.execute("""
        INSERT INTO notes (notes, carrier)
        VALUES (%s, %s)
        ON CONFLICT (notes) DO NOTHING;
    """, (notes, carrier_name))
