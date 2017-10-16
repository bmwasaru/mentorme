# mentor001 platform

## Set up for local development

### 1 Install Python 3.5.*, Django and PostgreSQL

**Python 3.5.x**
https://www.python.org/downloads/

**Django 1.11.x**
https://docs.djangoproject.com/en/1.11/intro/install/

**Redis Server**
https://redis.io/topics/quickstart

### 2 Clone the repository

Via https

    git clone https://github.com/Mentor001/platform.git

or via ssh

    git clone git@github.com:mentor001/platform.git

### 3 Install dependencies
On the project root there is a requirements.pip file. Make sure you install all the required dependencies before running Mentor001

    pip install -U -r requirements.txt

### 4 Set up local development
Copy the contents of `mentor001/local_settings.py.example` to a new file `mentor001/local_settings.py` and fill in the respective local database settings and generate a SECRET_KEY


**Note:** You can use Django methods to create a new SECRET_KEY https://github.com/django/django/blob/master/django/core/management/commands/startproject.py

### 5 Migrate

    python manage.py migrate

### 6 Run

    python manage.py runserver
