# mentor001 platform

## Set up for local development

### 1 Install Python 2.7, Django and PostgreSQL

**Python 3.5.x**
https://www.python.org/downloads/

**Django 1.11.x**
https://docs.djangoproject.com/en/1.11/intro/install/

### 2 Clone the repository

Via https

    git clone https://github.com/Mentor001/platform.git

or via ssh

    git clone git@github.com:mentor001/platform.git

### 3 Install dependencies
On the project root there is a requirements.pip file. Make sure you install all the required dependencies before running Bootcamp

    pip install -U -r requirements.txt

### 4 Python Decouple
As the project uses **[python-decouple][0]** you will need to create a file named **.env** on the root of the project with three values, as following:

    DEBUG=True
    SECRET_KEY='mys3cr3tk3y'
    DATABASE_URL='postgres://mentor001db_user:p4ssw0rd@localhost:5432/mentor001db'

**Note:** You can use Django methods to create a new SECRET_KEY https://github.com/django/django/blob/master/django/core/management/commands/startproject.py

### 5 Migrate

    python manage.py migrate

### 6 Run

    python manage.py runserver

[0]: https://github.com/henriquebastos/python-decouple
