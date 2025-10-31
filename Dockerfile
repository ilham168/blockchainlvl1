# Dockerfile

# Gunakan base image Python yang ringan (slim)
FROM python:3.10-slim

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# 1. Instal Dependencies
# Salin file requirements.txt
COPY requirements.txt .

# Instal semua dependensi Python.
RUN pip install --no-cache-dir -r requirements.txt
# BARIS BERIKUT DIHAPUS: RUN pip install ecdsa 

# 2. Salin Kode Sumber
# Salin semua isi folder src/ ke dalam /app/src/ di container
COPY src/ ./src/

# Salin juga file contoh yang mungkin diperlukan untuk testing/setup awal
COPY examples/ ./examples/

# 3. Ekspos Port
EXPOSE 8000

# 4. Command Default (Opsional, akan ditimpa oleh docker-compose)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]