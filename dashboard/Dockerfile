FROM python:3.11-slim

WORKDIR /app

# Copier les requirements et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code du dashboard
COPY . .

# Exposer les ports
EXPOSE 8501 8001

# Lancer Streamlit + FastAPI ensemble
CMD sh -c "uvicorn api:app --host 0.0.0.0 --port 8001 & streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"