FROM python:3.9

WORKDIR /app

# Python settings: Force unbuffered stdout and stderr (i.e. they are flushed to terminal immediately)
ENV PYTHONUNBUFFERED 1
# Python settings: do not write pyc files
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir -p /var/docforge/static

# Create the media and documents directories and set permissions
RUN mkdir -p /var/docforge/media /var/docforge/media/documents && \
    chown -R nobody:nogroup /var/docforge/media /var/docforge/media/documents && \
    chmod -R 775 /var/docforge/media /var/docforge/media/documents

# Keep the dependencies installation before the COPY of the app/ for proper caching
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app