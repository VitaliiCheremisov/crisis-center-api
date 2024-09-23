FROM python:3.10-slim

WORKDIR /app

RUN pip install gunicorn==21.0.1

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--access-logfile" , "-", "donor_base.wsgi"]
