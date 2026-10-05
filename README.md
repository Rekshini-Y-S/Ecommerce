#Ecommerce


##🌱 Green Fashion

Green Fashion is a Django-based e-commerce web application designed to promote sustainable and ethical fashion. The platform allows buyers to explore products with sustainability and ethical ratings, manage their shopping cart, and place orders, while sellers can manage products and view business analytics through a dedicated dashboard and API.

##🎯 Project Objective

The main objective of this project is to build an e-commerce platform that combines online fashion shopping with sustainability insights, helping users make more informed purchasing decisions based on product sustainability and ethical ratings.

##✨ Key Features

- Browse, search, and explore fashion products.
- View sustainability and ethical ratings for products.
- Category-based product recommendations.
- Separate Buyer and Seller registration and login portals.
- Add, review, and remove products from the shopping cart.
- Place and manage orders through the application.
- Upload product images or use images from external URLs.
- Seller dashboard with business and sales metrics.
- Seller analytics API secured with an API key.
- Green-fashion dataset and machine-learning resources included in the project.
- CNN-LSTM model artifact and Jupyter notebook included for experimentation.

«Note: Checkout currently records orders within the application and does not integrate with an external payment gateway.»

##🛠️ Technologies Used

Technology| Purpose
Python| Application development
Django 5.2| Web application framework
SQLite| Database
HTML & CSS| User interface
JavaScript| Client-side functionality
Pillow| Image upload and processing
Jupyter Notebook| Data analysis and experimentation
CNN-LSTM| Machine-learning model artifact

##📊 Analytics & Machine Learning

The project includes a green-fashion dataset and a Jupyter notebook for data analysis and experimentation.

The seller analytics API provides business metrics such as:

- Sales
- Orders
- Products
- Customers

The project also contains a CNN-LSTM model artifact related to the machine-learning component.

«The current Django storefront does not load the saved CNN-LSTM model during its normal request flow. The notebook can be executed separately for machine-learning experimentation.»

##🔌 Seller Analytics API

Authenticated sellers can generate an API key from the seller dashboard and use it to access seller-specific analytics.

Example Request

GET /seller/api/analytics/
Authorization: Api-Key <your-api-key>

The API returns JSON-based analytics for the authenticated seller.

##🖥️ Application Modules

###👤 Buyer Module

- Registration and login
- Product browsing and search
- Product details
- Cart management
- Checkout and order placement

###🏪 Seller Module

- Seller registration and login
- Product management
- Seller dashboard
- Sales and business metrics
- API key generation
- Analytics API

###📈 Analytics & ML Module

- Green-fashion dataset
- Data analysis notebook
- Seller analytics API
- CNN-LSTM model artifact

##🚀 Getting Started

###Requirements

- Python 3.10 or newer
- "pip"

1. Clone the Repository

git clone <repository-url>
cd Ecommerce

2. Create a Virtual Environment

python -m venv .venv

3. Activate the Virtual Environment

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

macOS / Linux:

source .venv/bin/activate

4. Install Dependencies

python -m pip install "Django>=5.2,<6.0" Pillow

5. Apply Database Migrations

python manage.py migrate

6. Create an Administrator Account

Optional:

python manage.py createsuperuser

7. Run the Development Server

python manage.py runserver

Open:

"http://127.0.0.1:8000/"

Django Admin:

"http://127.0.0.1:8000/admin/"

##🧭 Main Routes

Route| Purpose
"/"| Storefront
"/products/"| Product catalog
"/search/"| Product search
"/signup/"| Buyer registration
"/login/"| Buyer login
"/cart/"| Shopping cart
"/checkout/"| Checkout
"/seller/signup/"| Seller registration
"/seller/login/"| Seller login
"/seller/dashboard/"| Seller dashboard
"/seller/api/analytics/"| Seller analytics API
"/admin/"| Django administration

##📁 Project Structure

.
├── Ecommerce/          # Django project settings and URL configuration
├── website/            # Storefront, seller features, models, templates and static files
├── dataset/             # Green-fashion dataset, notebook and ML model
├── media/               # Uploaded media
├── product_images/      # Product image assets
├── db.sqlite3           # Local SQLite database
└── manage.py            # Django management script

##🧪 Testing

Run the Django test suite with:

python manage.py test

##🔐 Security & Deployment

The included Django settings are intended for local development.

Before deploying to production:

- Store "SECRET_KEY" securely using environment variables.
- Set "DEBUG=False".
- Configure "ALLOWED_HOSTS".
- Use a production-ready database.
- Configure static and media file handling.
- Never publish real credentials, private uploads, or sensitive data.




