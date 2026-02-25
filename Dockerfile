# ── STAGE: Runtime ───────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy only requirements.txt first → dependency layer gets cached.
# This layer won't be rebuilt on code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Start the application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
