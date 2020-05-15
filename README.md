# mentorme platform

## Set up for local development

### 1 Clone the repository

Via https

    git clone https://github.com/bmwasaru/mentorme.git

or via ssh

    git clone git@github.com:bmwasaru/mentorme.git

### 2 Install dependencies
On the project root there is a requirements.pip file. Make sure you install all the required dependencies before running Mentor001

    pipenv shell
    pipenv install

### 3 Set up local development
Copy the contents of `mentorme/local_settings.py.example` to a new file `mentorme/local_settings.py` and fill in the respective local database settings and generate a SECRET_KEY


**Note:** You can use Django methods to create a new SECRET_KEY https://github.com/django/django/blob/master/django/core/management/commands/startproject.py

### 4 Migrate

    python manage.py migrate

### 5 Run

    python manage.py runserver
