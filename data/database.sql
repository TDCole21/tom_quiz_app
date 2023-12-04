-- Database setup

-- From Windows
-- I created an EC2 instance running Linux, and saved the PEM file in this directory
-- Make sure the EC2 instance is running, then in VSCode terminal, run:
-- ssh -i "quiz-rds.pem" ubuntu@ec2-34-245-51-155.eu-west-1.compute.amazonaws.com
-- Note, when you stop and start the instance, it'll have a different IP address, so this code will need to be altered.
-- Then on the EC2 Linux instance, run the below linux command

-- From Linux
-- mysql -h quiz.cbpf0qmeaxbr.eu-west-1.rds.amazonaws.com -P 3306 -u admin -p
-- PaB98CeB65OaK91

-- On Local Machine
-- I installed mysql 8 on the machine and start the service
-- Then using credentials in info.py I connect to the database 


BEGIN;

CREATE DATABASE IF NOT EXISTS quiz;

USE quiz;

DROP TABLE IF EXISTS users, quizzes, categories, question_type, question_scoring_type, items, hints, participants, rounds, questions, live, answers, friends, user_media;

CREATE TABLE users (
    user_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    user_email VARCHAR(50) UNIQUE NOT NULL,
    user_password CHAR(225) NOT NULL,
    user_xp INT(3) NOT NULL,
    user_online BOOLEAN NOT NULL,
    user_admin BOOLEAN NOT NULL
    );

CREATE TABLE quizzes (
    quiz_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    quiz_name VARCHAR(50) UNIQUE NOT NULL,
    quiz_description TEXT NOT NULL
    );

CREATE TABLE categories (
    category_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    category_description TEXT
);

CREATE TABLE items (
    item_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    item_name VARCHAR(50) UNIQUE NOT NULL,
    item_description TEXT
);

CREATE TABLE question_type (
    question_type_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    question_type_name VARCHAR(50) UNIQUE NOT NULL,
    question_type_description TEXT
);

CREATE TABLE question_scoring_type (
    question_scoring_type_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    question_scoring_type_name VARCHAR(50) UNIQUE NOT NULL,
    question_scoring_type_description TEXT
);

-- Round category can be determined in code determined by categories of questions (mode or list for example)
CREATE TABLE rounds (
    round_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    round_name VARCHAR(50),
    round_description TEXT NOT NULL
);

-- Maybe put the urls in a separate table
CREATE TABLE questions (
    question_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    question_text TEXT,
    question_type_id INT(1),
    question_category_id INT(3),
    question_correct_answer TEXT,
    question_points INT(3),
    question_scoring_type_id INT(1),
    question_tag TEXT,
    question_difficulty INT (3),
    FOREIGN KEY(question_category_id) REFERENCES categories (category_id),
    FOREIGN KEY(question_scoring_type_id) REFERENCES question_scoring_type (question_scoring_type_id),
    FOREIGN KEY(question_type_id) REFERENCES question_type (question_type_id)
);

CREATE TABLE hints (
    hint_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    question_id INT(3) NOT NULL,
    hint_text TEXT NOT NULL,
    hint_number INT(3) NOT NULL,
    FOREIGN KEY(question_id) REFERENCES questions (question_id) ON DELETE CASCADE
);

-- This is a table of foreign keys that allows rounds and questions to be omnipotent.
-- This will allow you to add a previously made question to another quiz/round, and also previously made rounds to quizzes
CREATE TABLE live (
    quiz_id INT(3),
    quiz_active BOOLEAN,
    quiz_completed DATETIME,
    quiz_difficulty INT (3),
    round_id INT(3) NOT NULL,
    round_order INT(3),
    round_active BOOLEAN,
    round_completed BOOLEAN,
    question_id INT(3),
    question_order INT(3),
    question_active BOOLEAN,
    question_completed BOOLEAN,
    FOREIGN KEY(quiz_id) REFERENCES quizzes (quiz_id) ON DELETE CASCADE,
    FOREIGN KEY(round_id) REFERENCES rounds (round_id) ON DELETE CASCADE,
    FOREIGN KEY(question_id) REFERENCES questions (question_id) ON DELETE CASCADE
);


CREATE TABLE participants (
    user_id INT(3) NOT NULL,
    quiz_id INT(3) NOT NULL,
    participant_ready BOOLEAN,
    participant_score INT(3) NOT NULL,
    participant_position INT(3) NOT NULL,
    participant_item_id INT(3),
    FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    FOREIGN KEY(quiz_id) REFERENCES live (quiz_id) ON DELETE CASCADE,
    FOREIGN KEY(participant_item_id) REFERENCES items (item_id) ON DELETE CASCADE
);

CREATE TABLE answers (
    user_id INT(3) NOT NULL,
    question_id INT(3) NOT NULL,
    round_id INT(3) NOT NULL,
    quiz_id INT(3) NOT NULL,
    answer_text TEXT NOT NULL,
    answer_correct BOOLEAN,
    answer_points INT(3),
    answer_timestamp TIMESTAMP,
    hints_used INT(1),
    FOREIGN KEY(user_id) REFERENCES participants (user_id) ON DELETE CASCADE,
    FOREIGN KEY(question_id) REFERENCES questions (question_id) ON DELETE CASCADE,
    FOREIGN KEY(round_id) REFERENCES rounds (round_id) ON DELETE CASCADE,
    FOREIGN KEY(quiz_id) REFERENCES quizzes (quiz_id) ON DELETE CASCADE
);

CREATE TABLE friends (
    sender_id INT(3) NOT NULL,
    receiver_id INT(3) NOT NULL,
    accepted BOOLEAN NOT NULL,
    FOREIGN KEY(sender_id) REFERENCES users (user_id) ON DELETE CASCADE,
    FOREIGN KEY(receiver_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE user_media (
    user_media_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id INT(3) NOT NULL,
    user_media_url TEXT,
    user_media_type TEXT,
    user_media_description TEXT,
    FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE question_media (
    question_media_id INT(3) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    question_id INT(3) NOT NULL,
    question_media_url TEXT,
    question_media_type TEXT,
    question_media_description TEXT,
    FOREIGN KEY(question_id) REFERENCES questions (question_id) ON DELETE CASCADE
);

COMMIT;

-- Turns User 1 into an admin
UPDATE users SET user_admin = 1 WHERE user_id = 1;