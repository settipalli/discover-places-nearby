# Discover Places - Nearby

A location based service written in Python Flask that allows a user to discover nearby places of interest.

# Project Structure
    
    ├── Procfile
    ├── README.md
    ├── forms.py
    ├── models.py
    ├── requirements.txt
    ├── routes.py
    ├── static
    │   ├── README.md
    │   ├── css
    │   │   └── main.css
    │   └── img
    │       ├── README.md
    │       ├── device.svg
    │       ├── favicon.png
    │       ├── favicon.svg
    │       └── favicons
    │           ├── android-chrome-192x192.png
    │           ├── android-chrome-384x384.png
    │           ├── apple-touch-icon.png
    │           ├── browserconfig.xml
    │           ├── favicon-16x16.png
    │           ├── favicon-32x32.png
    │           ├── favicon.ico
    │           ├── manifest.json
    │           ├── mstile-150x150.png
    │           └── safari-pinned-tab.svg
    └── templates
        ├── README.md
        ├── about.html
        ├── home.html
        ├── index.html
        ├── layout.html
        ├── login.html
        └── signup.html
    

**routes.py**

Contains the applications main code.

**models.py**

Contains the `User` model class that represents the `users` table in the DB. Also contains the `Place` model that represents location data downloaded from external sources.

**forms.py**

Contains the Signup, Login and Address form backend implementation.

**requirements.txt**

Generated using `pip freeze` command. Contains the list of python packages that are required to be pre-installed for the application to execute without errors.

This file is also required for a successful heroku deployment.

**Procfile**

Contains a list of commands that inform heroku what to execute when the application is deployed so as to start the application.

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
6. Generate an API key for the project through `https://console.developers.google.com`
7. Save the API key as the `GOOGLE_API_KEY` config (environment) variable using the command: `heroku config:set GOOGLE_API_KEY=<key>`
8. Set the value of the `MODE` config (environment) variable as 'production' (without quotes) using the command: `heroku config:set MODE=production` and verify that the config variables are set appropriately using the command: `heroku config`
9. Push to heroku git repository: `git push heroku master`
10. Verify the deployment: `heroku open`
