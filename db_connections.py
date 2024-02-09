import logging

logging.basicConfig(level=logging.ERROR)

def create_carrier_info_table(cursor):
    table_schema = '''
    CREATE TABLE IF NOT EXISTS carrier_info (
        carrier_id SERIAL,
        carrier VARCHAR(255) UNIQUE PRIMARY KEY,
        carrier_name VARCHAR(255),
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
    INSERT INTO carrier_info (carrier, carrier_name, status, address, telephone, email_address, contact_person)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (carrier) DO NOTHING;
    '''
    cursor.execute(insert_query, data)


def create_drivers_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS drivers (
            sea_link VARCHAR(20),
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

        try:
            cursor.execute("""
                SELECT * FROM drivers WHERE name = %s AND carrier = %s;
            """, (name, carrier_name))
            existing_record = cursor.fetchone()

            if existing_record:
                cursor.execute("""
                    UPDATE drivers
                    SET sea_link = %s, auth = %s, name=%s, status = %s, relationship = %s
                    WHERE name = %s AND carrier = %s;
                """, (sea_link, auth, name, status, relationship, name, carrier_name))
            else:
                cursor.execute("""
                    INSERT INTO drivers (sea_link, auth, name, status, relationship, carrier)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (sea_link, auth, name, status, relationship, carrier_name))

        except Exception as e:
            logging.error("The data you are trying to update is not present in the database; insert it first.")
            logging.error(f"Error occurred: {e}")


def create_line_auth_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS line_auth (
            line VARCHAR(255),
            auth BOOLEAN,
            line_carrier VARCHAR(255),
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

        try:
            if auth:
                cursor.execute("""
                    SELECT * FROM line_auth WHERE line = %s and carrier = %s;
                """, (line ,carrier_name))

                existing_record = cursor.fetchone()
                if existing_record:
                    cursor.execute("""
                        UPDATE line_auth
                        SET line = %s, auth = %s, line_carrier = %s
                        WHERE line = %s and carrier = %s;
                    """, (line, auth, line_carrier, line, carrier_name))
                else:
                    cursor.execute("""
                        INSERT INTO line_auth (line, auth, line_carrier, carrier)
                        VALUES (%s, %s, %s, %s)
                    """, (line, auth, line_carrier, carrier_name))
        except Exception as e:
            logging.error("The data you are trying to update is not present in the database; insert it first.")
            logging.error(f"Error occurred: {e}")

def create_notes_table(cursor):
    table_schema = '''
        CREATE TABLE IF NOT EXISTS notes (
            notes VARCHAR(255),
            carrier VARCHAR(255),
            FOREIGN KEY(carrier) REFERENCES carrier_info(carrier)
        );
    '''
    cursor.execute(table_schema)


def insert_notes_data(cursor, notes, carrier_name):
    try:
        cursor.execute("""
            SELECT * FROM notes WHERE carrier = %s;
        """, (carrier_name,))

        existing_record = cursor.fetchone()

        if existing_record:
            cursor.execute("""
                UPDATE notes
                SET notes = %s
                WHERE carrier = %s;
            """, (notes, carrier_name))
        else:
            cursor.execute("""
                INSERT INTO notes (notes, carrier)
                VALUES (%s, %s)
            """, (notes, carrier_name))
    except Exception as e:
        logging.error("The data you are trying to update is not present in the database; insert it first.")
        logging.error(f"Error occurred: {e}")