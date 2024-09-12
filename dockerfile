# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /report

# Copy the current directory contents into the container at /name-project
COPY . /report

# Copy .env file into the container
COPY .env /report/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the python program
CMD ["python", "problems.py"]