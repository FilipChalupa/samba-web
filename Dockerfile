FROM python:3.12-slim

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY server.py /server.py

EXPOSE 80
ENV PORT=80

CMD ["python", "/server.py"]
