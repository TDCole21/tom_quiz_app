# Quiz App

This is a personal project to create a quiz web application. The idea has developed from hosting in-person yearly birthday quizzes, to remote quizes using Google Workspaces front end and a python backend, to finally hosting an application on public cloud services.


---

## Contents
1. [Brief](#brief)
    1. [Current Version](#current_features)
    2. [Next Steps](#next_steps)
    3. [Road Map](#feature_roadmap)
2. [Release Versions](#release_versions)
    1. [1.0.0](#1.0.0)
        1. [1.0.1](#1.0.1)
3. [Tech Stack](#tech_stack)
    1. [Infrastructure](#infrastructure)
    2. [Front End](#froint_end)
    3. [Back End](#back_end)
    4. [Database](#database)
    5. [Testing](#testing)
4. [Installation Guide](#installation)
5. [Authors](#authors)
6. [Acknowledgements](#acknowledgements)


## Brief <a name="brief"></a>
The idea of this Quiz App is to be a 24/7 hosted application, that allows users to create quizzes and host them with their friends.

### Current Version <a name="current_features"></a>
+ Users can create a personal profile featuring:
    + Username
    + Password
    + Email Address
+ Admin users can create quizes and host them
+ Users can join live quizes hosted by an admin user
+ Users can view the results of a quiz

### Next Steps v2.0 <a name="next_steps"></a>
+ Create more user profile options
+ Make the website more intuative to operate
+ Edit the submit answer section
+ More options for quiz creation

### Road Map <a name="feature_roadmap"></a>
+ Automated infrastructure deployment
+ Scalable deployment
+ Auto-generate Quiz
+ User ratings
+ Users friends
+ Containerisation

## Release Versions <a name="release_versions"></a>
Latest release V1.0.1 - 14/01/2022

### V1.0.0 <a name="1.0.0"></a>
##### Release Date
14th January 2022

##### Features
+ Users can now create, update, delete and view their own profile
+ User passwords are hashed in the database
+ Admin users can now create, update, delete and view quizes
+ Admin users can host live quizes and mark answers
+ Users can join live quizes

##### Known issues
+ Debug text on some pages
+ [Major Bug] Results page doesn't load
+ Embedded videos don't work
+ Image sizing issue

#### V1.0.1 <a name="1.0.1"></a>
##### Release Date
14th January 2022

##### Features
+ Successful first quiz

##### Bug Fixes
+ Users can now view results from quiz

##### Known issues
+ [Major Bug] User can submit answers for a different question as a different user


## Tech Stack <a name="tech_stack"></a>
### Infrastructure <a name="infrastructure"></a>
+ Quiz app hosted on EC2 T2.Micro instance on AWS
+ Database hosted on MySQL RDS on AWS
+ No infrastrucutre as code yet

### Front End <a name="front_end"></a>
+ Jinja2
+ HTML
+ CSS

### Back End <a name="back_end"></a>
+ Python
+ Flask

### Database <a name="database"></a>
+ MySQL

### Testing <a name="testing"></a>
+ No testing at the moment, other than QA

## Installation Guide <a name="installation"></a>
TBA

## Authors <a name="authors"></a>
Thomas Cole - DevOps Engineer

## Acknowledgements <a name="acknowledgements"></a>
I would like to acknowledge my partner Niamh Gill for their advice and motivation.