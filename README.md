# Django Auth Template with Tailwind CSS & DaisyUI

A modern Django project template with built-in authentication, user profiles, Tailwind CSS 4, and DaisyUI for rapid application development.

## Features

- **Complete User Authentication System**: Login, signup, password reset, email verification
- **User Profiles**: Customizable user profiles with image upload via Cloudinary
- **Modern UI**: Tailwind CSS 4 with DaisyUI components for beautiful interfaces
- **Responsive Design**: Fully mobile-responsive layouts
- **PostgreSQL Integration**: Configured for PostgreSQL in production
- **Django Admin Customization**: Enhanced admin interface with Unfold
- **Import/Export Support**: Easy data import/export capabilities

## Quick Start

### Prerequisites

- Python 3.x
- Node.js and npm
- PostgreSQL (for production) - db.sqlite3 is used for development

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/stephendawsondevconnection_engine.git
   cd connection_engine
   ```

2. **Set up a virtual environment**

   On Windows:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   On macOS/Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**

   ```bash
   npm install
   ```

5. **Create an env.py file**

   Create a file named `env.py` in the project root with the following content:

   ```python
   import os

   os.environ["DATABASE_URL"] = "sqlite:///db.sqlite3"  # For development
   os.environ["SECRET_KEY"] = "your-secret-key"
   os.environ["CLOUDINARY_URL"] = "your-cloudinary-url"  # Get from Cloudinary dashboard
   os.environ["ALLOWED_HOSTS"] = "*"
   os.environ["CSRF_TRUSTED_ORIGINS"] = "http://* https://*"
   os.environ["DEBUG_MODE"] = "True"
   ```

6. **Run database migrations**

   ```bash
   python manage.py migrate
   ```

7. **Start the Tailwind CSS watcher**

   In a separate terminal:

   ```bash
   npm run dev
   ```

8. **Run the development server**

   ```bash
   python manage.py runserver
   ```

9. **Access the application**

   Open your browser and go to <http://127.0.0.1:8000/>

## Using DaisyUI and Tailwind CSS

This template uses DaisyUI (a Tailwind CSS component library) along with Tailwind CSS 4 for styling.

### Recommended Approach

1. **Start with DaisyUI components**: DaisyUI provides pre-built components that are easy to use and customize. Check the [DaisyUI documentation](https://daisyui.com/components/) for available components.

2. **Customize with Tailwind utilities**: Extend and customize DaisyUI components using Tailwind utility classes as needed.

### Common DaisyUI Components for Beginners

- **Buttons**: `btn`, `btn-primary`, `btn-outline`, `btn-sm`, `btn-lg`
- **Cards**: `card`, `card-body`, `card-title`
- **Form elements**: `input`, `input-bordered`, `form-control`, `textarea`, `checkbox`, `label`
- **Alerts**: `alert`, `alert-info`, `alert-success`, `alert-warning`, `alert-error`
- **Navigation**: `navbar`, `menu`, `dropdown`
- **Layout**: `hero`, `container`, `divider`

### Useful Tailwind CSS Classes

- **Flex layouts**: `flex`, `flex-col`, `items-center`, `justify-between`, `gap-4`
- **Grid layouts**: `grid`, `grid-cols-1`, `md:grid-cols-3`, `gap-6`
- **Spacing**: `p-4`, `px-6`, `py-2`, `m-3`, `mt-4`, `mb-6`
- **Text**: `text-lg`, `font-bold`, `text-center`
- **Responsive design**: `sm:text-lg`, `md:flex-row`, `lg:grid-cols-3`
- **Colors**: `bg-base-100`, `text-primary`, `border-secondary`
- **Shadows**: `shadow-md`, `shadow-xl`
- **Rounding**: `rounded-lg`, `rounded-full`

## Theme Customization

DaisyUI provides multiple built-in themes. The template is configured with a light/dark theme toggle in the navigation.

## Deployment

For deployment, you will need the following environment variables:

```
DATABASE_URL = <your-production-database-url>
SECRET_KEY = <your-secret-key>
CLOUDINARY_URL = <your-production-cloudinary-url>
ALLOWED_HOSTS = <your-deployed-app-url>
CSRF_TRUSTED_ORIGINS = <your-deployed-app-url>
DEBUG_MODE = False
```
