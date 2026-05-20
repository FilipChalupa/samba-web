FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PORT=80

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY server.py /server.py

EXPOSE 80
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost/healthz')"

CMD ["python", "/server.py"]
