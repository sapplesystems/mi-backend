# Made In India Backend

This backend contains APIs for generating Made in India label for Products made in India

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

- docker (on mac install using `brew cask install docker`)

### Installing

Below is a step by step series of examples that tell you how to get a development env running.

```
#NOTE: To create a new project with this boilerplate
git clone <repository> <project_name>
cd <project_name>
rm -rf .git
git init
git remote add origin <your_project_git_url>
git add .
git commit -m <message>
git branch -M main
git push -u origin main

./scripts/start-container # starts a local terminal for local development
./scripts/migrate
./scripts/seed # if you want to seed the database from fixtures
./scripts/start-app
```

You should now see `Starting development server at http://0.0.0.0:8000/`

## Seed Database

Seed data can be kept in the fixtures directory. It can be stored as YAML or json, although I prefer YAML Example file
for users is included. It creates three users. One admin, admin@app.com, and two other test users. The following
commands load and dump data.

```
# load all fixtures
./scripts/seed

# load a specific fixture
./scripts/manage loaddata ./fixtures/users/user.yaml

# dump an apps data in a fixture
./scripts/manage dumpdata users.user --format=yaml > ./fixtures/users/user.yaml
```

## Running the tests

Example GraphQL tests have been added to the users app. To run those and future tests use the command below.

```
./scripts/manage test
```

## Installing New Packages

Dependencies are installed with pipenv. To install a new package simply run the command below. That will install it in
your current working container. The `./scripts/start-container` script will build the docker image from scratch so you
don't have to worry about running `pipenv install` when you start the container.

```
pipenv install <package_name>
```

## Useful Apps and their Documentation

Some apps come pre-installed in this boilerplate. Here is a list of them and a link to their documentation. You may want
to remove these if you don't want their functionality.

- [django-extentions](https://django-extensions.readthedocs.io/en/latest/installation_instructions.html) - Provides a
  bunch of useful commands for working in Django. For example, running `./scripts/manage shell_plus` will load a shell
  with all your models already loaded.
- [django-import-export](https://django-import-export.readthedocs.io/en/stable/) - Provides an import and export which
  can be useful in the admin tool.
- [django-simple-history](https://django-simple-history.readthedocs.io/en/latest/) - Provides a way to track changes to
  models. Useful for debugging and auditing which information has changed and by who. Simply
  add `history = HistoricalRecords()` on to one of your models. It also easily integrates with the admin tool.

## Benchmarking

```shell
pip3 install -r locust
# there are different scripts for each endpoint
# for testing post long url to get short url , go to benchmarking/create_short_url
cd benchmarking/get_url
# run the benchmarking script, for browser enabled machine
locust -f benchmark_with_get_url.py --host https://mi-backend.qci.solutions/

```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details



"# mi-backend" 
