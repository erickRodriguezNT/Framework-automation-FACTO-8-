# =============================================================================
# Dockerfile - Auto FACTO 8 Automation Framework
# =============================================================================
# Base: python:3.11-slim + Google Chrome Stable + ChromeDriver via webdriver-manager
# Para Cloud Run: build + push a Artifact Registry, deploy como Job (no servicio HTTP)
# =============================================================================

FROM python:3.11-slim

# --------------------------------------------------------------------------
# Variables de entorno globales
# --------------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99 \
    CHROME_BIN=/usr/bin/google-chrome \
    PIP_NO_CACHE_DIR=1

# --------------------------------------------------------------------------
# Dependencias del sistema + Google Chrome Stable
# --------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        ca-certificates \
        curl \
        unzip \
        xvfb \
        # Dependencias de Chrome
        libglib2.0-0 \
        libnss3 \
        libnspr4 \
        libdbus-1-3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libxkbcommon0 \
        libpango-1.0-0 \
        libcairo2 \
        libasound2 \
        fonts-liberation \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
        gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
        http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# Directorio de trabajo
# --------------------------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------------------------
# Instalar dependencias Python
# --------------------------------------------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# --------------------------------------------------------------------------
# Copiar el código fuente
# --------------------------------------------------------------------------
COPY . .

# --------------------------------------------------------------------------
# Crear directorios de salida
# --------------------------------------------------------------------------
RUN mkdir -p outputs/screenshots outputs/pdf outputs/xml \
             outputs/logs outputs/json outputs/zip \
             allure-results

# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------
RUN chmod +x docker/entrypoint.sh

ENTRYPOINT ["docker/entrypoint.sh"]
