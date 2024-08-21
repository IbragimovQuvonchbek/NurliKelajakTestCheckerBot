# Use the official Python image from the Docker Hub
FROM python:slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose any necessary ports (if your scripts require it)
# EXPOSE 8000

# Define the default command to run your application
CMD ["python", "run.py"]
