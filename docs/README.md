# Errander sample application

## Setup

Clone repository, create and activate virtual environment, install requirements, fill necessary settings in settings.py and run project

```sh
$ git clone https://github.com/karol-bekieszczuk/errander
$ cd errander
$ virtualenv venv
$ source venv/bin/activate
(env)$ pip install -r requirements.txt
```

### Development
To run with development settings fill GOOGLE_API_KEY in errander/settings/dev.py and run python smtp server with

```sh
python -m smtpd -n -c DebuggingServer localhost:1025
```

Next run server (development settings are loaded by default)

```sh
(env)$ python manage.py runserver
```

### Production
To run with production settings fill needed settings in errander/settings/prod.py and run the server with correct settings file

```sh
(env)$ python manage.py runserver --settings=errander.settings.prod.py
```
And navigate to `http://127.0.0.1:8000/accounts/login_user`.

TODO
