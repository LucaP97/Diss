# Diss

docker run -d -p 6379:6379 redis

celery -A mysite worker --loglevel=info

celery -A mysite beat