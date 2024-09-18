# Django Billable Hours

## Project Description
This web application allows law firms to generate client invoices based on the number of hours worked by employees. Lawyers submit their timesheets in CSV format, and the system calculates the total hours and generates an invoice for each client.

## Features
- Upload CSV timesheets
- Calculate billable hours per employee
- Generate invoices for each project
- Django admin for managing employees and projects

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/alemyaobed/billable-hours-invoicing.git
cd billable-hours-invoicing
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file and configure your database and secret keys.

### 4. Run the Application
```bash
python manage.py migrate
python manage.py runserver
```

### 5. Run Tests
```bash
python manage.py test
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
