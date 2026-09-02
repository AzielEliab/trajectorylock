FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
EXPOSE 8080
# Container bind is explicit. Local `trajectorylock ui` stays loopback-only.
CMD ["python", "-m", "trajectorylock.server", "--host", "0.0.0.0", "--port", "8080", "--allow-non-loopback"]
