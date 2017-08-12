# Discover Places - Nearby

A location based service written in Python Flask that allows a user to discover nearby places of interest.

# Project Structure

    ├── README.md
    ├── routes.py
    ├── static
    │   ├── README.md
    │   ├── css
    │   ├── img
    │   └── js
    └── templates
        └── README.md

**routes.py**

Contains the applications main code.

**static**

The application static files are stored in this folder.

**templates**

The application's HTML files are stored in this folder.

# Heroku deployment workflow

1. Install heroku toolbelt. Follow the steps outlined at: https://devcenter.heroku.com/articles/heroku-cli
2. Install `gunicorn`
3. Create requirements.txt using the command `pip freeze requirements.txt`  
4. Create `Procfile` with the below contents:

        web: gunicorn routes:app
    
5. Create a heroku app: `heroku create <appname>`
6. Push to heroku git repository: `git push heroku master`
7. Verify the deployment: `heroku open`
