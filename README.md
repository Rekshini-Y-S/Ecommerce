Ecommerce
# Green Fashion

## Project Overview

Green Fashion is a web-based fashion marketplace built with Django. It helps shoppers discover products with sustainability and ethical ratings, while giving sellers a separate portal to view store activity and sales analytics.

The application supports two types of users:

- **Buyers** can browse and search products, explore recommendations, manage a shopping cart, and place orders.
- **Sellers** can sign in to a dashboard, review store metrics, and use an API key to access analytics.

The project also includes green-fashion datasets, a Jupyter notebook, and a saved CNN-LSTM model as research assets. The Django storefront currently uses its database-backed product and recommendation views; it does not load the saved model during normal website requests.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Main Routes](#main-routes)
- [Seller Analytics API](#seller-analytics-api)
- [Tests](#tests)
- [Project Structure](#project-structure)
- [Security and Deployment](#security-and-deployment)

## Features

- Browse and search the product catalog, with product details and category-based recommendations.
- View sustainability and ethical scores alongside product information.
- Create separate buyer and seller accounts and sign in through the corresponding portals.
- Add products to a buyer cart, review or remove cart items, and place orders.
- Upload product images or display images from an external URL.
- View seller dashboard metrics and retrieve analytics using a seller API key.
- Explore the included green-fashion dataset, Jupyter notebook, and CNN-LSTM model artifact.

> Checkout currently records orders in the application; it does not integrate with an external payment provider.

## Tech Stack

- Python
- Django 5.2
- SQLite
- HTML, CSS, and JavaScript
- Pillow for uploaded image support

## Getting started

### Requirements

- Python 3.10 or newer
- `pip`

### Install and run

1. Clone the repository and open its directory:

   ```bash
   git clone <repository-url>
   cd Ecommerce
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   On Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install the application dependencies:

   ```bash
   python -m pip install "Django>=5.2,<6.0" Pillow
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. (Optional) Create an administrator account to manage products in Django admin:

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

Open <http://127.0.0.1:8000/> to visit the storefront. The Django admin is available at <http://127.0.0.1:8000/admin/>.

## Main routes

| Route | Purpose |
| --- | --- |
| `/` | Storefront |
| `/products/` | Product catalog |
| `/search/` | Search products |
| `/signup/`, `/login/` | Buyer registration and sign-in |
| `/cart/` | Buyer shopping cart |
| `/checkout/` | Checkout |
| `/seller/signup/`, `/seller/login/` | Seller registration and sign-in |
| `/seller/dashboard/` | Seller dashboard |
| `/seller/api/analytics/` | Seller analytics API (requires an API key) |
| `/admin/` | Django administration |

## Seller analytics API

Authenticated sellers can generate or regenerate an API key from the seller dashboard. Send the key in the `Authorization` header when requesting the analytics endpoint:

```http
GET /seller/api/analytics/
Authorization: Api-Key <your-api-key>
```

The endpoint returns JSON metrics for the seller, including sales, orders, products, and customers.

## Tests

Run the Django test suite with:

```bash
python manage.py test
```

## Project structure

```text
.
├── Ecommerce/     # Django project settings and root URL configuration
├── website/       # Storefront, seller features, models, templates, and static files
├── dataset/       # Green-fashion CSV files, notebook, and saved model
├── media/         # Uploaded media
├── product_images/# Product image assets
├── db.sqlite3     # Local SQLite database
└── manage.py
```

Running the notebook separately may require additional packages such as Jupyter, pandas, NumPy, scikit-learn, and TensorFlow.

## Security and deployment

The checked-in Django settings are intended for local development. Before deploying, configure a new `SECRET_KEY` through an environment variable, set `DEBUG=False`, configure `ALLOWED_HOSTS`, and use an appropriate production database and static/media-file setup. Do not publish or reuse real secrets, local databases, or private uploads.
