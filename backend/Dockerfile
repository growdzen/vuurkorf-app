FROM python:3.11-slim

WORKDIR /app

# System dependencies voor rembg, opencv, vtracer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directories worden aangemaakt via env vars in de app
RUN mkdir -p /opt/render/project/uploads /opt/render/project/outputs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
