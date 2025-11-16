"""
Sample Database Configuration for Biocat Interface
Copy this file to config.py and modify the settings for your environment
"""

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",  # Add your MySQL password here
    "database": "biocat",
    "charset": "utf8mb4",
    "use_unicode": True,
    "autocommit": True,
    "ssl_disabled": True,  # Set to False if using SSL
    "connect_timeout": 30,
    "read_timeout": 30,
    "write_timeout": 30,
}

# Alternative configuration for remote database
REMOTE_DB_CONFIG = {
    "host": "your-remote-host.com",
    "port": 3306,
    "user": "biocat_user",
    "password": "your_secure_password",
    "database": "biocat",
    "charset": "utf8mb4",
    "use_unicode": True,
    "autocommit": True,
    "ssl_ca": "/path/to/ca-cert.pem",  # SSL certificate path if needed
    "ssl_cert": "/path/to/client-cert.pem",
    "ssl_key": "/path/to/client-key.pem",
}

# Gradio interface settings
INTERFACE_CONFIG = {
    "server_name": "0.0.0.0",  # Use "127.0.0.1" for localhost only
    "server_port": 7860,
    "share": False,  # Set to True to create a public link
    "debug": False,
    "inbrowser": True,
    "auth": None,  # Set to ("username", "password") for authentication
    "max_threads": 40,
}

# Query execution limits
QUERY_LIMITS = {
    "default_limit": 100,
    "max_limit": 1000,
    "search_limit": 50,
    "max_search_limit": 200,
}

# Visualization settings
VIZ_CONFIG = {
    "default_plot_width": 800,
    "default_plot_height": 400,
    "color_palette": "husl",
    "dna_window_size": 50,
    "protein_window_size": 9,
}

# Security settings
SECURITY_CONFIG = {
    "allowed_query_types": ["SELECT"],
    "forbidden_keywords": [
        "DROP",
        "DELETE",
        "INSERT",
        "UPDATE",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
    ],
    "max_query_length": 5000,
    "enable_custom_queries": True,
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_to_file": False,
    "log_file_path": "biocat_interface.log",
    "max_log_size": 10485760,  # 10MB
    "backup_count": 5,
}

# Application metadata
APP_INFO = {
    "title": "Biocat Database Interface",
    "version": "1.0.0",
    "description": "Interactive web interface for exploring biological data",
    "author": "Biocat Team",
    "contact": "admin@biocat.org",
}

# Feature flags
FEATURES = {
    "enable_protein_analysis": True,
    "enable_dna_analysis": True,
    "enable_custom_queries": True,
    "enable_gene_search": True,
    "enable_visualizations": True,
    "enable_data_export": True,
    "show_query_preview": True,
    "auto_refresh_connection": True,
}

# Cache settings (for future use)
CACHE_CONFIG = {
    "enable_query_cache": False,
    "cache_ttl": 300,  # 5 minutes
    "max_cache_size": 100,
    "cache_backend": "memory",  # memory, redis, etc.
}

# Development settings
DEV_CONFIG = {
    "debug_mode": False,
    "show_sql_errors": True,
    "enable_profiling": False,
    "mock_data": False,
    "test_database": "biocat_test",
}

# How to use this configuration:
# 1. Copy this file to config.py
# 2. Modify the DB_CONFIG section with your database credentials
# 3. Adjust other settings as needed
# 4. Import in your application: from config import DB_CONFIG

# Example usage in database.py:
# try:
#     from config import DB_CONFIG
# except ImportError:
#     # Fallback to default configuration
#     DB_CONFIG = {
#         "host": "localhost",
#         "port": 3306,
#         "user": "root",
#         "password": "",
#         "database": "biocat"
#     }
