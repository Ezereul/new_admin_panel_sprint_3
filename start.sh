#!/bin/sh

echo "Проверяем Postgres"
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "БД запустили"

./create_index.sh

echo "Индекс создали"

while true; do
    echo "Поехали"
    python main.py
    echo "Все ок"
    sleep ${INTERVAL:-120}
done
