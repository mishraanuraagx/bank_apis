# Use official Python image as a base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Update pip and setuptools before installing dependencies
RUN pip install --upgrade pip setuptools

# Install dependencies for the application
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
