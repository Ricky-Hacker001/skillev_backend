# Use a tiny Python image
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Install Flask
RUN pip install flask

# Copy our app into the container
COPY app.py .

# Expose the port the app runs on
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]