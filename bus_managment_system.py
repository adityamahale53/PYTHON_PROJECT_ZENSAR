import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
from datetime import date, datetime
from decimal import Decimal

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "empdb"
}

# Get a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

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
            cursor = conn.cursor(dictionary=True)

            if self.path.startswith("/employees/"):
                employee_id = self.path.split("/")[-1]
                cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
                result = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM employees")
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
            sql = """
                INSERT INTO employees 
                (first_name, last_name, email, phone_number, hire_date, job_id, salary, manager_id, department_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data['first_name'],
                data['last_name'],
                data['email'],
                data['phone_number'],
                data['hire_date'],
                data['job_id'],
                data['salary'],
                data['manager_id'],
                data['department_id']
            )
            cursor.execute(sql, values)
            conn.commit()

            self.send_response(201)
            self._set_headers()
            self.end_headers()
            response = {"message": "Employee created successfully"}
            self.wfile.write(json.dumps(response).encode())
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
