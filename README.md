# SDWAN API

This project provides a FastAPI based REST service for automating Cisco SD-WAN deployments.

## Tech Stack

* **Backend**: FastAPI
* **HTTP Client**: httpx
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Validation**: Pydantic
* **Auth**: JWT / API Key
* **Task Queue**: BackgroundTasks (or Celery for larger workloads)
* **Testing**: pytest
* **Container**: Docker

## Features

1. **Authenticate** with Cisco SD-WAN Manager
2. **Send REST requests** to its endpoints
3. **Store deployment history/logs** in the database
4. **Expose clean APIs** for automation

## Getting Started

Refer to the source code configuration in `app/config.py` for environment variables.
