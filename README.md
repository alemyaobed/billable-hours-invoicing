# Django Billable Hours

## Project Description
This web application allows law firms to generate client invoices based on the number of hours worked by employees. Lawyers submit their timesheets in CSV format, and the system calculates the total hours and generates an invoice for each client.

## Features
- Upload CSV timesheets file
- Generate invoices for each project listed in the file

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
Create a `.env` file and configure your database, secret keys, celery broker url and your celery result backend.

### 4. Run the Application
```bash
python manage.py migrate
python manage.py runserver
```

### 5. Start Celery
Ensure you have a Celery broker installed (e.g., Redis or RabbitMQ). Start the broker, then run the following command in a new terminal:
```bash
celery -A <your_project_name> worker --loglevel=info
```
*Replace `your_project_name` with the actual name of your Django project. In this case billable_hours:*
```bash
celery -A your_project_name worker --loglevel=info
```

### 6. Run Tests
Make sure the celery process is already started
```bash
python manage.py test
```


### 7. Deployment
Before deploying the application, ensure to run the following command to collect static files:
```bash
python manage.py collectstatic
```
This command gathers all static assets into the specified directory for serving in production.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
