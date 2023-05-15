ARG BASE=ubuntu
ARG VERSION=latest

FROM ${BASE}:${VERSION}

# Set the working directory
WORKDIR /app

# Update packages and install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Install flaskr
#RUN pip3 install .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install .

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
