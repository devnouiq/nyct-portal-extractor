def create_carrier_info_table(cursor):
    table_schema = '''
    CREATE TABLE IF NOT EXISTS carrier_info (
        carrier_id SERIAL PRIMARY KEY,
        carrier VARCHAR(255) UNIQUE,
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

def update_data_in_carrier_info_table(cursor, carrier_id, data):
    update_query = '''
    UPDATE carrier_info
    SET carrier = %s, status = %s, address = %s, telephone = %s, email_address = %s, contact_person = %s
    WHERE carrier_id = %s;
    '''
    cursor.execute(update_query, (*data, carrier_id))


def create_drivers_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS drivers (
            driver_id SERIAL PRIMARY KEY,
            sea_link VARCHAR(20),
            auth BOOLEAN,
            name VARCHAR(255),
            status VARCHAR(255),
            relationship VARCHAR(255)
        );
    '''
    cursor.execute(table_schema)

def insert_data_into_drivers_table(cursor, drivers):
    for key, value in drivers.items():
        sea_link = value['SeaLink']
        auth = value['Auth'] == 'true'
        name = value['Name']
        status = value['Status']
        relationship = value['Relationship']

        cursor.execute("INSERT INTO drivers (sea_link, auth, name, status, relationship) VALUES (%s, %s, %s, %s, %s)",
                (sea_link, auth, name, status, relationship))
        
def update_data_in_drivers_table(cursor, driver_id, driver_data):
    update_query = '''
    UPDATE drivers
    SET sea_link = %s, auth = %s, name = %s, status = %s, relationship = %s
    WHERE driver_id = %s;
    '''
    cursor.execute(update_query, (*driver_data, driver_id))


def create_line_auth_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS line_auth (
            line_auth_id SERIAL PRIMARY KEY,
            line VARCHAR(255),
            auth BOOLEAN,
            line_carrier VARCHAR(255)
        );
    '''
    cursor.execute(table_schema)

def insert_data_into_line_auth_table(cursor, line_auth):
    for key, value in line_auth.items():
        line = value[0]
        auth = value[1] == 'true'
        line_carrier = value[2]
        cursor.execute("INSERT INTO line_auth (line, auth, line_carrier) VALUES (%s, %s, %s)", (line, auth, line_carrier))

def update_data_in_line_auth_table(cursor, line_auth_id, line_auth_data):
    update_query = '''
    UPDATE line_auth
    SET line = %s, auth = %s, line_carrier = %s
    WHERE line_auth_id = %s;
    '''
    cursor.execute(update_query, (*line_auth_data, line_auth_id))


def create_notes_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS notes (
            note_id SERIAL PRIMARY KEY,
            notes VARCHAR(255)
        );
    '''
    cursor.execute(table_schema)

def insert_notes_data(cursor, notes):
    cursor.execute("INSERT INTO notes (notes) VALUES (%s)", (notes,))


def update_notes_data(cursor, note_id, new_notes):
    update_query = '''
    UPDATE notes
    SET notes = %s
    WHERE note_id = %s;
    '''
    cursor.execute(update_query, (new_notes, note_id))
