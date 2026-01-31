FROM python:3.11-slim

WORKDIR /app

# Install fonts and graphics libraries (libEGL for skia/pictex)
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    libegl1 \
    libgl1 \
    libgles2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p outputs/generated outputs/composed

CMD ["python", "main.py"]