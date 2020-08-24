# GA_Exercise

Gamer Arena Exercise backend project

## Installment

To install with Docker, execute following command

`make build`

### Docker
All of the structure runs on docker environment. Please follow the official docker [installment guides](https://docs.docker.com/install/).

### Environment variables

Settings gets required configurations from .env files. `.env` is used by `local.yml`

### Run
Most used docker commands are placed in a Makefile
- To run tests:
  - `make build` and `make test-users`
- To run django server:
  - `make build` and `make up`
- To access shell:
  - `make plus` or `make shell-web`
- To create default superuser with following credentials (username= "admin@ga.com", password="awesome123"):
  - `make create-superuser`
  
## Folder Structure

Main folders:
 - bin
   - runnable scripts to manage deployment
 - compose
   - docker compose configurations
 - config
   - django settings and urls
 - requirements
   - requirement files based on environments
 - ga_exercise
   - **main django project**
   