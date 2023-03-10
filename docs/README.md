# Errander sample application

This is sample application allowing users to create and assign errands to users.

## Setup

Clone repository, create and activate virtual environment, install requirements, fill necessary settings in settings files and run project

```sh
$ git clone https://github.com/karol-bekieszczuk/errander
$ cd errander
$ virtualenv venv
$ source venv/bin/activate
(venv)$ pip install -r requirements.txt
```

### Development
The development environment uses MySQL as database and needs some SMTP server to validate emails.
To run with development settings fill GOOGLE_API_KEY in errander/settings/dev.py. 

Run python SMTP server (this step is optional, but allows mail validation)

```sh
python -m smtpd -n -c DebuggingServer localhost:1025
```

Next run server (development settings are loaded by default)

```sh
(venv)$ ./manage.py runserver
```

### Production
The production environment uses PostgreSQL as database and Gmail as mail provider.

Fixtures are provided to create users:
  * Admin(superuser)
  * PrivilegedUser(user with all custom user and errand permissions)
  * DefaultUser(user with default permissions)

Run fixtures with
```sh
(venv)$ ./manage.py loaddata accounts/accounts.json --settings=errander.settings.prod
```

To run with production settings fill neecessary settings in errander/settings/prod.py and run the server with correct settings file

```sh
(venv)$ ./manage.py runserver --settings=errander.settings.prod
```

Then navigate to `http://127.0.0.1:8000/accounts/login_user` to log in.

## Walkthrough

### Users
Users with default permissions can log in and view their profile page, assigned errands and change or reset password.

Users with appropriate permissions can view the index of users, details and send invites to app by registering new user and sending them activation link. If user clicks on link within 24 hours from creation user gets activated, otherwise link get expired and user is deleted by cron job on database side, this project in production uses PostgreSQL with [citusdata/pg_cron](https://github.com/citusdata/pg_cron) lib.


### Errands
User with default permissions can list their own errands in profile or errand index template, then update and/or change its status.

Users with appropriate permissions can create new errands and assign users to it, list every errand in database and change its assigned users.

Every errand has assigned users, name, description, status, address and geolocation on which bases Google map displayed in new and detail errand templates.

Errand history is archived by [jazzband/django-simple-history](https://github.com/jazzband/django-simple-history) and available to download in .csv format, or by clicking on "Show history" button in errand detail template.

## Tests

To run the tests, `cd` into the directory where `manage.py` is:
```sh
(venv)$ python manage.py test 
```
