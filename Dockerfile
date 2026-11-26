FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd --create-home appuser

# Copy required project files
COPY --chown=appuser:appuser manage.py .
COPY --chown=appuser:appuser urls.py .
COPY --chown=appuser:appuser admin_app/ ./admin_app/
COPY --chown=appuser:appuser mediplus/ ./mediplus/
COPY --chown=appuser:appuser user_app/ ./user_app/
COPY --chown=appuser:appuser templates/ ./templates/
COPY --chown=appuser:appuser static/ ./static/

# Copy media if required
COPY --chown=appuser:appuser media/ ./media/

USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]