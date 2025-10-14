import psycopg2

host = "vultr-prod-80a17e4a-5490-47fc-a39c-af19d2daf2db-vultr-prod-ec67.vultrdb.com"
port = 16751
database = "defaultdb"
user = "vultradmin"
password = "AVNS_DMvzJGmUnhuykNdherM"

BATCH_SIZE = 50  # commit mỗi 50 ward một lần

try:
    conn = psycopg2.connect(
        host=host, port=port, database=database, user=user, password=password
    )
    cursor = conn.cursor()
    print("Connected to PostgreSQL successfully!")

    cursor.execute("SELECT id, geology FROM ward WHERE geom IS NULL;")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} wards to update...")

    counter = 0

    for key, row in enumerate(rows):
        ward_id = row[0]
        geo_json = row[1]

        if not geo_json or "coordinates" not in geo_json:
            print(f"ward {ward_id} has no coordinates, skipping...")
            continue

        coords = geo_json["coordinates"]

        # Lấy polygon đầu tiên (GeoJSON có thể là MultiPolygon)
        ring = coords[0]

        # Chuyển dict {'lat':..., 'lng':...} sang list [lng, lat] và loại bỏ None
        ring = [[pt['lng'], pt['lat']] for pt in ring if pt.get('lng') is not None and pt.get('lat') is not None]

        # Kiểm tra đủ điểm
        if len(ring) < 4:
            print(f"ward {ward_id} has too few points, skipping...")
            continue

        # Đảm bảo polygon "đóng"
        if ring[0] != ring[-1]:
            ring.append(ring[0])

        # Tạo WKT Polygon string
        polygon_coords = ", ".join([f"{lng} {lat}" for lng, lat in ring])
        wkt = f"POLYGON(({polygon_coords}))"

        try:
            cursor.execute(
                "UPDATE ward SET geom = ST_GeomFromText(%s, 4326) WHERE id = %s;",
                (wkt, ward_id)
            )
        except Exception as e:
            print(f"Failed to update ward {ward_id}: {e}")
            conn.rollback()  # rollback bản ghi lỗi, tiếp tục ward khác
            continue

        counter += 1

        # Commit theo batch
        if counter % BATCH_SIZE == 0:
            conn.commit()
            print(f"Committed {counter} wards so far...")

        print(f"Success {key}: ward_id {ward_id}")

    # Commit lần cuối nếu còn dư
    conn.commit()

    cursor.close()
    conn.close()
    print("Update geom finished!")

except Exception as e:
    print("Error connecting to PostgreSQL:", e)