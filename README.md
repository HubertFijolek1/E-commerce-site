# E-commerce Cart System

This project is a simple e-commerce cart system built with Django. It allows users to browse products, add them to a cart, apply discounts, and manage multiple carts like wishlists or shopping lists.

## Features

1. **Add to Cart with Quantity Selection**
   - Users can add products to the cart with a specified quantity.

2. **Remove Items from Cart**
   - Items can be removed individually from the cart.

3. **Update Item Quantity**
   - Quantities of items in the cart can be updated directly from the cart page.

4. **Apply Discount Codes**
   - Discount codes can be applied during checkout to receive discounts on the total price.

5. **Display Total Price Including Taxes and Shipping**
   - The cart displays the subtotal, discounts, taxes, shipping costs, and final total price.

6. **Session-Based Cart for Guest Users**
   - Guests can add items to a session-based cart without logging in. Their cart data is stored in the session.

7. **Persist Cart for Logged-In Users**
   - Logged-in users have their cart data saved in the database, allowing them to access their cart across multiple sessions and devices.

8. **Validate Stock Before Adding to Cart**
   - The system checks if enough stock is available before adding items to the cart or updating quantities.

9. **Multiple Carts for Users**
   - Users can create multiple carts, such as wishlists or shopping lists, and switch between them.

10. **Clear Entire Cart**
    - Users can clear all items from their cart with a single action.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ecommerce_site
```

Replace `<repository-url>` with the URL of your Git repository.

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install django
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user for accessing the Django admin site.

### 6. Run the Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and navigate to `http://localhost:8000/`.

## Running Tests

To run the unit tests for the cart application:

```bash
python manage.py test cart
```

## Project Structure

- `ecommerce_site/` - Main Django project directory.
- `cart/` - Django app containing models, views, templates, and URLs for the cart system.
- `templates/` - Directory for shared templates.
- `static/` - Directory for static files like CSS.
- `manage.py` - Django's command-line utility for administrative tasks.

## Requirements

- Python 3.x
- Django 3.x or higher

## Additional Information

### Database Configuration

The project uses SQLite by default, but you can configure other databases like PostgreSQL or MySQL in `ecommerce_site/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Change this to your preferred database engine
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

### Static Files

During development, static files are served automatically. For production, you need to collect static files and configure your web server accordingly:

```bash
python manage.py collectstatic
```

### User Authentication

The project uses Django's built-in authentication system. You can customize authentication templates and views as needed.

### Admin Site

You can manage products, discount codes, and view carts through the Django admin site. Access it at `http://localhost:8000/admin/` and log in with the superuser account you created.
