#!/usr/bin/env python3
"""Fullstack Development - Python: 65 MCQ questions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from seed_data.common import make_mcq, insert_domain_questions

DOMAIN = "Fullstack Development - Python"

questions = [
    # ── EASY (20) ──────────────────────────────────────────────
    make_mcq(
        "Which Python web framework follows the 'batteries-included' philosophy?",
        ["Flask", "FastAPI", "Django", "Bottle"],
        "C", "Easy"),
    make_mcq(
        "What command creates a new Django project?",
        ["django-admin startproject", "django new project", "python manage.py createproject", "pip create django"],
        "A", "Easy"),
    make_mcq(
        "In Django, which file defines URL routing patterns?",
        ["views.py", "models.py", "urls.py", "settings.py"],
        "C", "Easy"),
    make_mcq(
        "What does ORM stand for in the context of Django?",
        ["Object Relational Mapping", "Object Resource Manager", "Oriented Relation Model", "Open Request Mapper"],
        "A", "Easy"),
    make_mcq(
        "Which command applies Django database migrations?",
        ["python manage.py makemigrations", "python manage.py migrate", "python manage.py syncdb", "python manage.py dbupdate"],
        "B", "Easy"),
    make_mcq(
        "In FastAPI, which Python type hint feature is used for request validation?",
        ["dataclasses", "Pydantic models", "TypedDict", "NamedTuple"],
        "B", "Easy"),
    make_mcq(
        "What is the default template engine used by Django?",
        ["Jinja2", "Mako", "Django Template Language (DTL)", "Chameleon"],
        "C", "Easy"),
    make_mcq(
        "Which HTTP status code indicates a successful POST request that created a resource?",
        ["200 OK", "201 Created", "204 No Content", "301 Moved"],
        "B", "Easy"),
    make_mcq(
        "In Django, where is the database configuration specified?",
        ["models.py", "urls.py", "settings.py", "views.py"],
        "C", "Easy"),
    make_mcq(
        "What is the purpose of Django's admin.py file?",
        ["Define URL patterns", "Register models for the admin interface", "Configure middleware", "Define database schemas"],
        "B", "Easy"),
    make_mcq(
        "Which tool is commonly used to manage Python virtual environments?",
        ["npm", "pip only", "virtualenv or venv", "conda only"],
        "C", "Easy"),
    make_mcq(
        "In Django REST Framework, which class is used to convert model instances to JSON?",
        ["ModelForm", "Serializer", "JSONRenderer", "Paginator"],
        "B", "Easy"),
    make_mcq(
        "What does CSRF stand for in web security?",
        ["Cross-Site Request Forgery", "Client-Side Request Failure", "Cross-Server Response Format", "Common Security Resource Framework"],
        "A", "Easy"),
    make_mcq(
        "Which decorator makes a Python function an API endpoint in FastAPI?",
        ["@api.route", "@app.get or @app.post", "@endpoint", "@route"],
        "B", "Easy"),
    make_mcq(
        "In Django, which directory typically holds CSS, JS, and image files?",
        ["templates/", "static/", "media/", "assets/"],
        "B", "Easy"),
    make_mcq(
        "What is Gunicorn?",
        ["A JavaScript bundler", "A Python WSGI HTTP server", "A CSS framework", "A database driver"],
        "B", "Easy"),
    make_mcq(
        "Which file in a Django app defines the database schema using Python classes?",
        ["views.py", "admin.py", "models.py", "forms.py"],
        "C", "Easy"),
    make_mcq(
        "What does the `pip freeze` command output?",
        ["Installed packages and their versions", "System hardware info", "Python version number", "Available package updates"],
        "A", "Easy"),
    make_mcq(
        "In Django, what is the purpose of the {% block %} template tag?",
        ["Creates a for loop", "Defines overridable sections in template inheritance", "Imports static files", "Creates conditional logic"],
        "B", "Easy"),
    make_mcq(
        "Which Python package manager supports dependency groups and lock files natively?",
        ["pip", "easy_install", "Poetry", "setuptools"],
        "C", "Easy"),

    # ── MEDIUM (30) ─────────────────────────────────────────────
    make_mcq(
        "In Django REST Framework, what is the difference between a ModelSerializer and a Serializer?",
        [
            "ModelSerializer is faster; Serializer is deprecated",
            "ModelSerializer auto-generates fields from a model; Serializer requires explicit field definitions",
            "Serializer supports nested objects; ModelSerializer does not",
            "They are identical"
        ],
        "B", "Medium"),
    make_mcq(
        "How does FastAPI achieve automatic API documentation?",
        [
            "Manual Markdown files",
            "Generates OpenAPI schema from type hints and Pydantic models",
            "Requires Sphinx documentation tool",
            "Uses Django admin for documentation"
        ],
        "B", "Medium"),
    make_mcq(
        "In Django, what is the purpose of the MEDIA_ROOT setting?",
        [
            "Path for compiled static assets",
            "Directory for user-uploaded files",
            "Path for Django template files",
            "Directory for migration files"
        ],
        "B", "Medium"),
    make_mcq(
        "Which Django middleware handles CSRF token validation?",
        ["SessionMiddleware", "CsrfViewMiddleware", "AuthenticationMiddleware", "SecurityMiddleware"],
        "B", "Medium"),
    make_mcq(
        "In a FastAPI + React integration, what is the typical development setup to avoid CORS issues?",
        [
            "Both run on the same port",
            "Configure CORSMiddleware in FastAPI to allow the React dev server origin",
            "Disable browser security",
            "Use server-side rendering only"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Django Channels?",
        [
            "Database connection pooling",
            "Adds WebSocket, long-polling, and async protocol support to Django",
            "Email sending functionality",
            "Static file compression"
        ],
        "B", "Medium"),
    make_mcq(
        "In SQLAlchemy, what does session.commit() do?",
        [
            "Rolls back all changes",
            "Flushes pending changes and commits the transaction to the database",
            "Creates a new database session",
            "Closes the database connection"
        ],
        "B", "Medium"),
    make_mcq(
        "Which Celery component acts as the message broker?",
        [
            "Celery worker",
            "Celery beat",
            "RabbitMQ or Redis",
            "Django ORM"
        ],
        "C", "Medium"),
    make_mcq(
        "In Django, how do you create a custom management command?",
        [
            "Add a function to views.py",
            "Create a file in management/commands/ with a Command class extending BaseCommand",
            "Define it in settings.py",
            "Add it to urls.py"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the difference between session-based and token-based authentication in a Python fullstack app?",
        [
            "Session stores state on the server; tokens are stateless and stored on the client",
            "Tokens are always less secure than sessions",
            "Sessions work only with REST APIs; tokens work only with GraphQL",
            "There is no difference"
        ],
        "A", "Medium"),
    make_mcq(
        "In Django REST Framework, what does the IsAuthenticated permission class do?",
        [
            "Allows all requests",
            "Denies access to unauthenticated users",
            "Checks if the user is a superuser",
            "Validates CSRF tokens"
        ],
        "B", "Medium"),
    make_mcq(
        "Which pytest fixture is commonly used to set up a Django test database?",
        [
            "@pytest.fixture(db=True)",
            "@pytest.mark.django_db",
            "@pytest.fixture(scope='database')",
            "@pytest.mark.use_db"
        ],
        "B", "Medium"),
    make_mcq(
        "In Jinja2 templating, what does the {{ variable | safe }} filter do?",
        [
            "Encrypts the variable",
            "Marks the variable as safe HTML, preventing auto-escaping",
            "Validates the variable type",
            "Converts the variable to a string"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Django's collectstatic command?",
        [
            "Compiles Python files to bytecode",
            "Gathers all static files into STATIC_ROOT for production serving",
            "Creates database backups",
            "Generates API documentation"
        ],
        "B", "Medium"),
    make_mcq(
        "In FastAPI, what is a Depends() used for?",
        [
            "Defining database models",
            "Dependency injection for shared logic like DB sessions or auth",
            "Importing third-party packages",
            "Defining URL path parameters"
        ],
        "B", "Medium"),
    make_mcq(
        "Which Nginx directive is used to proxy requests to a Gunicorn backend?",
        [
            "server_name", "proxy_pass", "listen", "root"
        ],
        "B", "Medium"),
    make_mcq(
        "In Django forms, what does the clean() method do?",
        [
            "Removes HTML tags from input",
            "Performs custom cross-field validation on form data",
            "Deletes form data from memory",
            "Formats form labels"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the role of the ASGI interface used by FastAPI?",
        [
            "Synchronous-only request handling",
            "Asynchronous Server Gateway Interface for handling async requests",
            "Database migration management",
            "Static file serving"
        ],
        "B", "Medium"),
    make_mcq(
        "In Django, what does the select_related() queryset method do?",
        [
            "Deletes related objects",
            "Performs a SQL JOIN to fetch related ForeignKey objects in one query",
            "Selects specific columns",
            "Groups query results"
        ],
        "B", "Medium"),
    make_mcq(
        "How do you handle file uploads in Django views?",
        [
            "Access files via request.GET",
            "Access files via request.FILES and save using model FileField/ImageField",
            "Files are auto-saved to the database",
            "Use a separate file server API"
        ],
        "B", "Medium"),
    make_mcq(
        "In a Django + Vue.js fullstack app, how is Vue typically integrated?",
        [
            "Vue replaces Django's ORM",
            "Vue is served as a separate SPA consuming Django REST API endpoints",
            "Vue templates replace Django templates one-to-one",
            "Vue runs on the server alongside Django"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Django's signals framework?",
        [
            "Sending HTTP signals to external APIs",
            "Allowing decoupled applications to get notified of certain actions (e.g., post_save)",
            "Managing WebSocket connections",
            "Handling interrupt signals in the OS"
        ],
        "B", "Medium"),
    make_mcq(
        "In SQLAlchemy, what is the purpose of the relationship() function?",
        [
            "Creates database indexes",
            "Defines how ORM classes relate to each other for easier querying",
            "Establishes HTTP connections",
            "Manages migration versions"
        ],
        "B", "Medium"),
    make_mcq(
        "Which Django setting should be set to False in production for security?",
        [
            "INSTALLED_APPS", "DEBUG", "ALLOWED_HOSTS", "DATABASES"],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of alembic in a FastAPI/SQLAlchemy project?",
        [
            "API documentation generation",
            "Database schema migration management",
            "Request validation",
            "Authentication handling"
        ],
        "B", "Medium"),
    make_mcq(
        "In Django REST Framework, what is a ViewSet?",
        [
            "A template for rendering views",
            "A class that combines logic for multiple related views (list, create, retrieve, update, delete)",
            "A set of database views",
            "A collection of URL patterns"
        ],
        "B", "Medium"),
    make_mcq(
        "Which Docker directive is used to run Gunicorn as the container's main process?",
        [
            "RUN gunicorn ...",
            "CMD [\"gunicorn\", \"...\"]",
            "EXPOSE gunicorn",
            "ENTRYPOINT pip install gunicorn"
        ],
        "B", "Medium"),
    make_mcq(
        "In Django, what is the difference between null=True and blank=True on a model field?",
        [
            "They are identical",
            "null=True allows NULL in the database; blank=True allows empty form submissions",
            "blank=True affects the database; null=True affects forms",
            "null=True is for integers; blank=True is for strings"
        ],
        "B", "Medium"),
    make_mcq(
        "What does the @login_required decorator do in Django views?",
        [
            "Creates a new user account",
            "Redirects unauthenticated users to the login page",
            "Validates CSRF tokens",
            "Enables API key authentication"
        ],
        "B", "Medium"),
    make_mcq(
        "In pytest, what does the --cov flag enable?",
        [
            "Verbose output", "Code coverage reporting", "Parallel test execution", "Test discovery"
        ],
        "B", "Medium"),

    # ── HARD (15) ───────────────────────────────────────────────
    make_mcq(
        "In Django, what is the difference between select_related() and prefetch_related()?",
        [
            "select_related is for async queries; prefetch_related is synchronous",
            "select_related uses SQL JOINs for ForeignKey/OneToOne; prefetch_related uses separate queries for ManyToMany/reverse FK",
            "select_related fetches all fields; prefetch_related fetches specific fields",
            "They are aliases for the same operation"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Django Channels use ASGI to handle WebSocket connections?",
        [
            "It falls back to WSGI for WebSocket support",
            "It uses an ASGI server (e.g., Daphne) with consumers that handle connect, receive, and disconnect events",
            "It converts WebSocket to HTTP long-polling automatically",
            "Django Channels only supports Server-Sent Events"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the Global Interpreter Lock (GIL) issue when scaling Python web applications, and how is it mitigated?",
        [
            "GIL prevents multi-threading for CPU tasks; mitigated with multi-process workers (Gunicorn with multiple workers) or async I/O",
            "GIL prevents database access; mitigated with connection pooling",
            "GIL limits memory usage; mitigated with garbage collection tuning",
            "GIL does not affect web applications"
        ],
        "A", "Hard"),
    make_mcq(
        "In FastAPI, what is the advantage of using async def over def for route handlers?",
        [
            "async def is always faster",
            "async def allows non-blocking I/O operations, freeing the event loop for concurrent requests",
            "def is not supported in FastAPI",
            "async def automatically parallelizes CPU-bound tasks"
        ],
        "B", "Hard"),
    make_mcq(
        "How should Celery tasks handle idempotency to prevent duplicate processing?",
        [
            "By running tasks synchronously",
            "By using unique task IDs, database-level deduplication, or idempotency keys",
            "By disabling retries entirely",
            "By using a single worker process"
        ],
        "B", "Hard"),
    make_mcq(
        "In Django, what is the purpose of the ContentType framework?",
        [
            "Managing HTTP Content-Type headers",
            "Enabling generic relations by tracking all models installed in the project",
            "Handling file MIME types",
            "Compressing response content"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the difference between Django's TestCase and TransactionTestCase?",
        [
            "TestCase is faster; TransactionTestCase is deprecated",
            "TestCase wraps tests in a transaction and rolls back; TransactionTestCase commits and truncates, allowing testing of transaction behavior",
            "TransactionTestCase does not support database operations",
            "They are identical in behavior"
        ],
        "B", "Hard"),
    make_mcq(
        "In a production FastAPI deployment, what is the role of uvicorn workers behind Nginx?",
        [
            "Uvicorn handles static files; Nginx handles API requests",
            "Uvicorn runs the ASGI app; Nginx serves as reverse proxy for TLS termination, load balancing, and static file serving",
            "Nginx replaces uvicorn entirely",
            "Uvicorn is only used in development"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Django's prefetch_related use the Prefetch object for custom querysets?",
        [
            "It cannot customize the prefetched queryset",
            "The Prefetch object allows specifying a custom queryset with filters, annotations, or ordering for the prefetched relation",
            "Prefetch object is used for caching only",
            "Prefetch object defines database indexes"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the N+1 query problem in Django ORM, and how does it manifest?",
        [
            "It causes database deadlocks",
            "Accessing related objects in a loop triggers one query per object instead of a batch query, degrading performance",
            "It prevents database connections from being reused",
            "It occurs only with raw SQL queries"
        ],
        "B", "Hard"),
    make_mcq(
        "In Django REST Framework, how do you implement nested serializer writes (creating parent and child in one request)?",
        [
            "Nested writes work automatically with ModelSerializer",
            "Override the create() or update() method in the serializer to handle nested data manually",
            "Use a separate endpoint for each nested resource",
            "Use raw SQL queries"
        ],
        "B", "Hard"),
    make_mcq(
        "What security risk does the Django setting ALLOWED_HOSTS mitigate?",
        [
            "SQL injection attacks",
            "HTTP Host header attacks that could lead to cache poisoning or password reset poisoning",
            "Cross-site scripting (XSS)",
            "Brute force login attempts"
        ],
        "B", "Hard"),
    make_mcq(
        "In SQLAlchemy, what is the difference between a scoped_session and a regular Session?",
        [
            "scoped_session is faster",
            "scoped_session provides thread-local session management, ensuring one session per thread",
            "Regular sessions support async; scoped sessions do not",
            "There is no practical difference"
        ],
        "B", "Hard"),
    make_mcq(
        "How does FastAPI handle request validation errors, and how can the error response format be customized?",
        [
            "It silently ignores invalid data",
            "It raises RequestValidationError (422 response) which can be customized via an exception handler registered with app.exception_handler()",
            "Validation errors always return 500",
            "It redirects to an error page"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the purpose of Django's database router, and when would you use one?",
        [
            "Routes HTTP requests to different views",
            "Directs database reads/writes to different databases in a multi-database setup",
            "Manages URL routing",
            "Handles WebSocket message routing"
        ],
        "B", "Hard"),
]

if __name__ == "__main__":
    insert_domain_questions(DOMAIN, questions)
