import json
import csv
import io
import zipfile
import database
from sqlalchemy import text

def _get_all_table_data(table_name):
    try:
        with database.engine.connect() as conn:
            # SQLAlchemy text() for raw SQL queries if we really want to just dump
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            keys = result.keys()
            return [dict(zip(keys, row)) for row in result]
    except Exception as e:
        print(f"Error reading table {table_name}: {e}")
        return []

def export_data_json():
    """Exports all user data as a JSON string."""
    tables = [
        "assessments",
        "appliances",
        "solar_configs",
        "user_challenges",
        "unlocked_badges",
        "xp_transactions",
        "journey_profiles",
        "offset_transactions"
    ]
    data = {}
    for table in tables:
        data[table] = _get_all_table_data(table)
    return json.dumps(data, indent=4)

def export_data_csv_zip():
    """Exports assessments, appliances, and offset_transactions as CSVs in a ZIP archive."""
    tables_to_export = ["assessments", "appliances", "offset_transactions"]
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for table in tables_to_export:
            data = _get_all_table_data(table)
            if not data:
                continue
            
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
            zip_file.writestr(f"{table}.csv", csv_buffer.getvalue())
            
    return zip_buffer.getvalue()

def import_data_json(json_str, strategy='merge'):
    """Imports JSON data back into the database. Strategy can be 'merge' or 'replace'."""
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return False, "Invalid JSON file format."

    # Validate schema loosely
    expected_tables = [
        "assessments", "appliances", "solar_configs", 
        "user_challenges", "unlocked_badges", "xp_transactions", 
        "journey_profiles", "offset_transactions"
    ]
    if not isinstance(data, dict):
        return False, "Invalid JSON data structure."
        
    for table, rows in data.items():
        if table not in expected_tables:
            continue
        if not isinstance(rows, list):
            return False, f"Invalid data format for table {table}."
            
    try:
        with database.engine.begin() as conn:
            for table, rows in data.items():
                if table not in expected_tables:
                    continue
                    
                if strategy == 'replace':
                    conn.execute(text(f"DELETE FROM {table}"))
                    
                for row in rows:
                    if not row:
                        continue
                    
                    if strategy == 'merge':
                        ts_col = None
                        if 'created_at' in row:
                            ts_col = 'created_at'
                        elif 'date' in row:
                            ts_col = 'date'
                        elif 'enrolled_at' in row:
                            ts_col = 'enrolled_at'
                        elif 'unlocked_at' in row:
                            ts_col = 'unlocked_at'
                            
                        if ts_col:
                            result = conn.execute(text(f"SELECT 1 FROM {table} WHERE {ts_col} = :ts"), {"ts": row[ts_col]})
                            if result.fetchone():
                                continue # Skip duplicate
                                
                    columns = ', '.join(row.keys())
                    placeholders = ', '.join([f":{k}" for k in row.keys()])
                    
                    try:
                        conn.execute(text(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"), row)
                    except Exception:
                        # Ignore unique constraint violations during merge
                        continue

        return True, "Data imported successfully!"
    except Exception as e:
        return False, f"Import failed: {str(e)}"
