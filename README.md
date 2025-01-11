# Bus Management System

This project is a Bus Management System that provides RESTful APIs to interact with a MySQL database, allowing users to manage employee records associated with a bus service. It is implemented using Python and MySQL.

## Features

- Fetch employee details by ID or list all employees.
- Add new employee records.
- Handle data types like `date`, `datetime`, and `decimal` with custom JSON encoding.
- Cross-Origin Resource Sharing (CORS) enabled for better integration with web applications.

## Project Structure

1. **`bus_managment_system.py`**  
   Contains the backend API logic implemented using Python's `http.server` module. This script allows you to:
   - Retrieve employee details via GET requests.
   - Add employee records via POST requests.

2. **`Bus_management_system.sql`**  
   The SQL file contains the database schema and initial data setup for the MySQL database. It should include tables such as `employees` and any related structures.

## Prerequisites

- Python 3.7 or later
- MySQL Server
- Python packages:
  - `mysql-connector-python`

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/Bus-Management-System.git
   cd Bus-Management-System
