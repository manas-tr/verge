FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pandas \
    numpy \
    scikit-learn \
    xgboost \
    mlflow \
    joblib


EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]