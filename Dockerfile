FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=4000

# Create uploads directory if not exists
RUN mkdir -p /app/uploads

# Expose the port the app runs on
EXPOSE 4000

# Command to run the application
CMD ["python", "app.py"]
