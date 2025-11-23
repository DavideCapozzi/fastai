# Best Practice: Usa Python Slim (Debian Bookworm) per leggerezza e stabilità
FROM python:3.11-slim-bookworm

# Evita buffering dei log python (utile per vedere errori in tempo reale)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 1. Installazione Dipendenze di Sistema
# graphviz: richiesto da fastai per visualizzare la struttura dei modelli
# git: per clonare repo o installare pacchetti git
# libgl1: richiesto da opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    graphviz \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Creazione Utente non-root (Best Practice di Sicurezza)
# Evita problemi di permessi sui file salvati sul tuo computer host
RUN useradd -m -s /bin/bash fastuser
WORKDIR /home/fastuser/project

# 3. Installazione PyTorch (Step Critico)
# Lo facciamo prima dei requirements per sfruttare la cache di Docker se cambiano solo le altre lib
# --no-cache-dir: mantiene l'immagine piccola
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 4. Installazione Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Impostiamo l'utente
USER fastuser

# 5. Configurazione Jupyter
# Espone la porta
EXPOSE 8888

# Avvio
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
