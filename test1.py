import psycopg2
import time
from concurrent.futures import ThreadPoolExecutor

lat = 10.797056
lon = 106.7024384

conn = psycopg2.connect(
    host="vultr-prod-80a17e4a-5490-47fc-a39c-af19d2daf2db-vultr-prod-ec67.vultrdb.com",
    port=16751,
    database="devdb",
    user="vultradmin",
    password="AVNS_DMvzJGmUnhuykNdherM"
)
cursor = conn.cursor()

# Helper function to run district query
def fetch_district(province_id, lon, lat):
    query_district = """
    SELECT id, name
    FROM district
    WHERE province_id = %s
      AND ST_Contains(geom, ST_SetSRID(ST_Point(%s, %s), 4326));
    """
    cursor.execute(query_district, (province_id, lon, lat))
    return cursor.fetchall()

# Helper function to run ward query
def fetch_ward(district_id, lon, lat):
    query_ward = """
    SELECT id, name
    FROM ward
    WHERE district_id = %s
      AND ST_Contains(geom, ST_SetSRID(ST_Point(%s, %s), 4326));
    """
    cursor.execute(query_ward, (district_id, lon, lat))
    return cursor.fetchall()

# Start the timer for the whole process
start_total_time = time.time()

# 1️⃣ Tìm province chứa point
query_province = """
SELECT id, name
FROM province
WHERE ST_Contains(geom, ST_SetSRID(ST_Point(%s, %s), 4326));
"""
cursor.execute(query_province, (lon, lat))
province_rows = cursor.fetchall()

if not province_rows:
    print("Point is not inside any province.")
else:
    for province in province_rows:
        province_id, province_name = province
        print(f"Point is inside province: {province_name} (id={province_id})")

        # Use ThreadPoolExecutor to run district and ward queries concurrently
        with ThreadPoolExecutor() as executor:
            # Start parallel queries for district and ward
            district_future = executor.submit(fetch_district, province_id, lon, lat)
            ward_futures = []  # Store ward futures for each district
            district_rows = district_future.result()

            if district_rows:
                for district in district_rows:
                    district_id, district_name = district
                    print(f"Point is inside district: {district_name} (id={district_id})")
                    
                    # Fetch wards for this district
                    ward_futures.append(executor.submit(fetch_ward, district_id, lon, lat))

                # Collect the ward results
                for ward_future in ward_futures:
                    ward_rows = ward_future.result()

                    if ward_rows:
                        for ward in ward_rows:
                            print(f"Point is inside ward: {ward[1]} (id={ward[0]})")
                    else:
                        print("Point is not inside any ward of this district.")
            else:
                print("Point is not inside any district of this province.")

# Calculate the total time for the whole process
end_total_time = time.time()
elapsed_total_ms = (end_total_time - start_total_time) * 1000
print(f"Total execution time: {elapsed_total_ms:.2f} ms")

cursor.close()
conn.close()