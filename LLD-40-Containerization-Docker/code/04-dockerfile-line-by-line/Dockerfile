# The finished file — identical to Dockerfile.7, under its real name.
# This is the guide page's "Simple Django Dockerfile": one instruction per layer,
# ordered least- to most-frequently-changing so the cache does its job.
#
#   docker build -t lineby .
#   docker run --rm -p 8000:8000 lineby
#   curl localhost:8000

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
