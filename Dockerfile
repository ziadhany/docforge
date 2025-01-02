FROM python:3.9

WORKDIR /app

# Python settings: Force unbuffered stdout and stderr (i.e. they are flushed to terminal immediately)
ENV PYTHONUNBUFFERED 1
# Python settings: do not write pyc files
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir -p /var/docforge/static

# Keep the dependencies installation before the COPY of the app/ for proper caching
COPY requirements.txt /app/
RUN pip install . -c requirements.txt

COPY . /app