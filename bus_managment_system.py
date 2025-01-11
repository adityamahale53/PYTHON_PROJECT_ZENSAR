import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import oracledb
from datetime import date, datetime
from decimal import Decimal

# Database Configuration
DB_CONFIG = {
    "host": "localhost",  # Replace with your Oracle DB host
    "port": 1521,         # Default Oracle port
    "sid": "XE",        # Your Oracle SID (or service name)
    "user": "system",  # Replace with your Oracle username
    "password": "root"  # Replace with your Oracle password
}

# Get a database connection
def get_db_connection():
    dsn = oracledb.makedsn(DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["sid"])
    connection = oracledb.connect(user=DB_CONFIG["user"], password=DB_CONFIG["password"], dsn=dsn)
    return connection

# Custom JSON encoder to handle special data types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()  # Convert to ISO 8601 string
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        return super().default(obj)

# Request Handler
class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()
        self.end_headers()

    def do_GET(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if self.path.startswith("/buses/"):
                bus_id = self.path.split("/")[-1]
                cursor.execute("SELECT * FROM buses WHERE bus_id = :bus_id", {"bus_id": bus_id})
                result = cursor.fetchone()
            elif self.path.startswith("/routes/"):
                route_id = self.path.split("/")[-1]
                cursor.execute("SELECT * FROM routes WHERE route_id = :route_id", {"route_id": route_id})
                result = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM buses")
                result = cursor.fetchall()

            response_body = json.dumps(result, cls=CustomJSONEncoder)
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            self.wfile.write(response_body.encode())
        except Exception as e:
            self.send_error(500, str(e))
        finally:
            cursor.close()
            conn.close()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            conn = get_db_connection()
            cursor = conn.cursor()

            # Example for booking insertion
            if self.path.startswith("/bookings"):
                sql = """
                    INSERT INTO bookings (passenger_id, schedule_id, seats_booked, total_amount)
                    VALUES (:passenger_id, :schedule_id, :seats_booked, :total_amount)
                """
                cursor.execute(sql, {
                    "passenger_id": data['passenger_id'],
                    "schedule_id": data['schedule_id'],
                    "seats_booked": data['seats_booked'],
                    "total_amount": data['total_amount']
                })
                conn.commit()
                
                self.send_response(201)
                self._set_headers()
                self.end_headers()
                response = {"message": "Booking created successfully"}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(400, "Invalid path")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

# Run the HTTP server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
