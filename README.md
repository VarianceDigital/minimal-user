# Minimal Flask + Boostrap 5 + User Authentication Demo Project 

## Overview

In this repo you'll find the source code for a small Flask + Boostrap 5 project, where data is managed via a **PostgreSQL** database.

The project implements *Minimal+User*, a demo application featuring a gallery of cat images and showcasing a complete and up-and-running flow for **USER AUTHENTICATION** and **USER AUTHORIZATION** .

This Flask application includes:
- basic user sign-up, login, logout mechinisms (and forms);
- recover forgot/lost access keys (passwords);
- automatic nickname, access key (password) and icon avatar generation for the user;
- a user profile section which enables to change the above-mentioned user data; 
- email confirmation mechanisms for all crucial use cases.

Please feel free to play with our demo, or learn more about this project (+ many other interesting things we are currently working on :) ).
We will be glad if you clone the repo as a starting point for your future awesome application.

It is quite easy to install *Minimal+User* on platforms like Azure and Heroku, and make it up and running on the Internet. Learn more reading this article.

This project is built "on top" of our **Minimal-DB Project**, please have a look: the repo is here, there is a working demo here, and instructions here).

    
## Requirements and specifications
- The site make use of the Flask session;
- It requires PostgreSQL as database engine;
- It uses AWS S3 buckets to save user's tile avatars.

### Packages needed are listed in requirements.txt
All packages needed to run this app are listed in the requirements.txt file.
To install, first activate your virutal environment and then launch:

``pip install -r requirements.txt``


## Project structure, page structure
For further explanations see the following article:
https://medium.com/@rinaldo.nani/flask-bootstrap-5-starter-web-sites-1f1237a85e83

