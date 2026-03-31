FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt ./

# Create a virtual environment and install dependencies into it
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000
EXPOSE 5000

# Set the working directory to the 'server' folder
WORKDIR /app/server

# Set environment variables so Python uses the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Run the application
CMD ["python", "app.py"]
