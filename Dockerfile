FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 빌드 시점에는 SECRET_KEY 등 실제 값이 없다 — collectstatic만 통과하면 되므로
# 더미 값으로 채운다 (whitenoise가 manifest를 만들려면 settings가 로드는 돼야 함).
RUN SECRET_KEY=build-time-placeholder DEBUG=False python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--log-file", "-"]
