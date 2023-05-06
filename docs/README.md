# Errander sample application

This is sample application allowing users to create and assign errands to users.

## Setup

Clone repository, and run docker compose up command with --build flag

```sh
$ git clone https://github.com/karol-bekieszczuk/errander
$ cd errander
$ docker compose up --build
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
