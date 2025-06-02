swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "HR System API",
        "description": "API documentation for HR system",
        "contact": {
            "email": "danangekasaputra@outlook.com",
            "url": ""
        },
        "version": "1.0.0"
    },
    "host": "backend.dandevlabs.my.id", #activate when on server
    "basePath": "/hrsystemapi/api/v1",
    "schemes": ["https"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            # "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            "description": "Enter your token with the `Bearer` prefix. Example: `Bearer eyJhbGci...`"
        }
    },
    "security": [
        {
            "BearerAuth": []
        }
    ]
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/hrsystemapi/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/hrsystemapi/",
}