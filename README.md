# Server Configuration Calculator

A Django-based web application for planning and managing server configurations, including hardware components, software licenses, and project management features.

## Features

- Hardware component management (CPUs, RAM, Storage, GPUs, Network Cards)
- Software license tracking and pricing
- Project planning and approval workflows
- Saved configuration templates
- Sample data loader for testing and demonstration

## Technologies & Libraries

### Backend
- **Django 5.1.4** - Web framework
- **Python 3.10+** - Programming language
- **SQLite** - Default database (can be configured for PostgreSQL)

### Frontend
- **Bootstrap 5.3.3** - CSS framework for responsive design
- **Tailwind CSS 3.4.17** - CSS framework for responsive design
- **jQuery 3.4.1** - JavaScript library
- **Font Awesome** - Icon library
- **Select2** - Enhanced select boxes

### Development Tools
- **django-debug-toolbar** - Debug toolbar for development
- **iommi 7.8.0** - Framework for building Django apps
- **asgiref 3.8.1** - ASGI utilities
- **sqlparse 0.5.3** - SQL parsing and formatting
- **typing-extensions 4.12.2** - Type hinting support
- **setuptools 59.6.0** - Package development tools
- **pip 22.0.2** - Package installer

### Key Django Components Used
- Django Admin
- Django Forms
- Django ORM
- Django Template Language
- Django Management Commands

## Prerequisites

- Python 3.10+
- pip
- virtualenv or venv
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hunterhines34/server-config-calculator.git
   cd server-config-calculator
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

6. Load sample data (optional):
   ```bash
   python manage.py load_sample_data
   ```
   This will populate the database with sample manufacturers, components, and configurations for testing.

7. Run the development server:
   ```bash
   python manage.py runserver
   ```
   The application will be available at `http://127.0.0.1:8000/`

## Deployment Options

### Option 1: Local Development
[Previous installation steps 1-7 remain unchanged]

### Option 2: Docker Deployment

Prerequisites:
- Docker
- Docker Compose
- SSL Certificate (for HTTPS)

1. Clone the repository:
   ```bash
   git clone https://github.com/hunterhines34/server-config-calculator.git
   cd server-config-calculator
   ```

2. Create SSL certificates (for development only):
   ```bash
   mkdir certs
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/server.key -out certs/server.crt
   ```
   For production, use proper SSL certificates from a certificate authority.

3. Create required directories:
   ```bash
   mkdir -p nginx/conf.d
   mkdir -p staticfiles
   mkdir -p media
   ```

4. Build and start the containers:
   ```bash
   docker compose up -d --build
   ```

5. Create a superuser:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. Load sample data (optional):
   ```bash
   docker compose exec web python manage.py load_sample_data
   ```

The application will be available at:
- HTTPS: https://localhost
- HTTP will automatically redirect to HTTPS

### Docker Volumes
The Docker setup includes three persistent volumes:
- `sqlite_data`: Database storage
- `static_volume`: Static files
- `media_volume`: User-uploaded media files

### Docker Services
- `web`: Django application with Gunicorn
- `nginx`: Web server for static files and reverse proxy

### Stopping the Docker Stack
```bash
# Stop the stack
docker compose down

# Remove all data (including database)
docker compose down -v
```

### Docker Environment Variables
You can customize the deployment by setting these environment variables:
- `DEBUG`: Set to 1 for development, 0 for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DJANGO_SETTINGS_MODULE`: Path to Django settings module

Example .env file:
```env
DEBUG=0
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=calculator.settings
```

## Sample Data

The sample data loader (`load_sample_data.py`) creates:

- Manufacturers (Intel, AMD, NVIDIA, etc.)
- CPUs (Intel Xeon, AMD EPYC)
- RAM modules (DDR4, DDR5)
- Storage devices (NVMe, SSD)
- Network cards
- GPU options
- License metrics and products
- Sample projects and configurations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django Framework
- Bootstrap/Tailwind for frontend styling
- Font Awesome for icons

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 