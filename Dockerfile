# ----------
# Project TIM – Phase 1+2 Docker image
# ----------
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m timuser

WORKDIR /home/timuser/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY nginx/nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /home/timuser/nginx/run /home/timuser/nginx/log \
    && chmod +x run.sh \
    && chown -R timuser:timuser /home/timuser/app /home/timuser/nginx

EXPOSE 8080

USER timuser

CMD ["./run.sh"]
