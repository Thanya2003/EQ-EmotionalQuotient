# Use a lightweight Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 5000

# Start the application
CMD ["python", "index.py"]
