# Use the official Python image
FROM python:3.12-slim@sha256:af4e85f1cac90dd3771e47292ea7c8a9830abfabbe4faa5c53f158854c2e819d

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./streamlit /app

# Install the required packages
RUN pip install -r requirements.txt

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]