# labs/web_dev/crud-api-lab/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install standard libraries the student might need
RUN pip install flask flask-sqlalchemy

COPY app.py .

# Create the DB file within the container
RUN touch task_manager.db

EXPOSE 5000

CMD ["python", "app.py"]