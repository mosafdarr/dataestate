import psycopg2

# Define the DATABASE dictionary
DATABASE = {
    'drivername': 'postgresql',
    'host': 'localhost',
    'port': '5432',
    'username': 'postgres',
    'password': 'crackitifyoucan123',
    'database': 'dataestate_db'
}

def fetch_country_and_cities(country_name):
    try:
        # Connect to the PostgreSQL database using the DATABASE dictionary
        connection = psycopg2.connect(
            host=DATABASE['host'],
            database=DATABASE['database'],
            user=DATABASE['username'],
            password=DATABASE['password'],
            port=DATABASE['port']
        )
        cursor = connection.cursor()

        # SQL query to fetch country and respective cities
        query = """
            SELECT c.name AS country_name, ci.name AS city_name
            FROM countries c
            JOIN cities ci ON ci.country_id = c.id
            WHERE c.name = %s;
        """
        cursor.execute(query, (country_name,))

        # Fetch all results
        result = cursor.fetchall()

        # Format the output
        if result:
            print(f"Country: {result[0][0]}")
            print("Cities:")
            for row in result:
                print(f"- {row[1]}")
        else:
            print(f"No cities found for country: {country_name}")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching data: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Example usage:
fetch_country_and_cities('UAE')
