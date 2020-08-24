build:
	docker-compose build
up:
	docker-compose up -d
stop:
	docker-compose stop
restart:
	docker-compose restart
restart-web:
	docker-compose restart django
log:
	docker-compose logs -f --tail 100
log-web:
	docker-compose logs -f --tail 100 django
shell-web:
	docker-compose run --rm django bash
plus:
	docker-compose run --rm django python manage.py shell_plus
migrations:
	docker-compose run --rm django python manage.py makemigrations
migrate:
	docker-compose run --rm django python manage.py migrate
test-users:
	docker-compose run --rm django python manage.py test users.tests
create-superuser:
	docker-compose run --rm django python manage.py runscript create_default_superuser

