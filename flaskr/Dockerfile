FROM python:3.9-slim-buster

WORKDIR /app

# Install dependencies
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt


# Copy the application code
COPY . .

RUN pip install -e .

# Set the environment variables
ENV FLASK_APP=flaskr
ENV FLASK_ENV=development
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Initialize the database
RUN flask init-db

# Expose port 5000
EXPOSE 5000

# Start the application
CMD ["flask", "run", "--host", "0.0.0.0"]
