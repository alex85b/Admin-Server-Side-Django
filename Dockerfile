# Pull base image
FROM python:3.9

# Set environment variables, console buffering and prevents python cache files being written
# python logs goes to container logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy local project files to container
COPY . /app

# Run server
CMD python manage.py runserver 0.0.0.0:8000