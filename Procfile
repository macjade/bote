release: python manage.py migrate
web: daphne bote.asgi:application --port $PORT --bind 0.0.0.0 -v2
boteworker: python manage.py runworker --settings=bote.settings -v2