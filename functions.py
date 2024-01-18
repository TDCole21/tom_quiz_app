#######################################################################################################################################################################
# PACKAGES
#######################################################################################################################################################################
# This section imports different packages required for the functions to work

from data import info
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from MySQLdb.cursors import DictCursor
import os
import re
import time
from werkzeug.security import generate_password_hash, check_password_hash
from multidict import MultiDict
import hashlib
import random



######################################################################################################################################################################
# MYSQL SETUP
######################################################################################################################################################################
# This section sets up the connection between the app and the mysql database hosted on a public cloud

# __name__ is for best practice
app = Flask(__name__) 

# Enter your database connection details below
app.config["MYSQL_DB"] = info.mysql_db
app.config["MYSQL_HOST"] = info.mysql_host
app.config["MYSQL_PASSWORD"] = info.mysql_password
app.config["MYSQL_USER"] = info.mysql_user

# Change this to your secret key (can be anything, it's for extra protection)
# This was to get flask flash to work
app.config['SECRET_KEY'] = 'something only you know' 


# Initialise MySQL
mysql = MySQL(app)


######################################################################################################################################################################
# FUNCTIONS
######################################################################################################################################################################
# These functions are independent 

# This functions checks if two values are identical
def duplicate(value1,value2):
    if value1 == value2:
        return True
    else:
        return False

# This function checks if a string contains an @ symbol.
# I use the @ symbol as an unique characteristic of email addresses, so this can be used to determine if a string is an email address
def email(test_string):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.search(email_pattern, test_string)

# This function returns the current time and date
def timestamp():
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


######################################################################################################################################################################
# SESSION
######################################################################################################################################################################
# These functions use the session feature of flask

# This function checks to see if the user currently logged in is an admin
def admin_check():
    if session['user_admin'] == 0:
        flash("You do not have the required authorisation")
        return False
    else:
        return True

# This function logs a user into the lession
def login_session(user_id, username, user_email, user_admin):
    session['loggedin'] = True
    session['user_id'] = user_id
    session['username'] = username
    session['user_email'] = user_email
    session['user_admin'] = user_admin

# This function logs a user out of the lession
def logout_session(): # clears all session information
    # session.pop('loggedin', None)
    # session.pop('user_id', None)
    # session.pop('username', None)
    # session.pop('user_email', None)  
    # session.pop('user_admin', None) 
    session.clear()

# This function determines how you logged into your account
def login_method(method):
    if email(method):
        Login_Via = "user_email"

    else:
        Login_Via = "username"


######################################################################################################################################################################
# QUIZ
######################################################################################################################################################################
# These functions are specific to the Quiz



######################################################################################################################################################################
# MYSQL
######################################################################################################################################################################
# These functions perform different mySQL queries

# This function checks if a value is in the database and returns True or False
def check_single_db(output, table, conditions):
    cur = mysql.connection.cursor()
    cur.execute("SELECT %s FROM %s WHERE %s" % (output, table, conditions))
    mysql.connection.commit()
    output = cur.fetchone()
    cur.close()    
    if output:
        return True
    else:
        return False
    
def count(table, column, value):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(%s) FROM %s WHERE %s = %s" % (column, table, column, value))
    mysql.connection.commit()
    output = cur.fetchone()
    cur.close() 
    return output

def count_not(table, column, value):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(%s) FROM %s WHERE %s != %s" % (column, table, column, value))
    mysql.connection.commit()
    output = cur.fetchone()
    cur.close() 
    return output

def check_multiple_db_not_unique(output, table1, common_column, table2, conditions): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT %s FROM %s WHERE %s IN (SELECT %s FROM %s WHERE %s)" % (output, table1, common_column, common_column, table2, conditions))
    mysql.connection.commit()
    output = cur.fetchone()
    cur.close()    
    if output:
        return True
    else:
        return False

def check_multiple_db(output, table1, table2, table1_column_name, table2_column_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT %s FROM %s INNER JOIN %s ON %s = %s" % (output, table1, table2, table1_column_name, table2_column_name))
    mysql.connection.commit()
    output = cur.fetchone()
    cur.close()    
    if output:
        return True
    else:
        return False
    

# This function selects common values between two tables
def common_values(output, table1, table2, table1_column_name, table2_column_name):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s INNER JOIN %s ON %s = %s" % (output, table1, table2, table1_column_name, table2_column_name))
    mysql.connection.commit()    
    data = cur.fetchall()
    cur.close()   
    return data

# This function selects common values between two tables
def common_value(output, table1, table2, table1_column_name, table2_column_name):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s INNER JOIN %s ON %s = %s" % (output, table1, table2, table1_column_name, table2_column_name))
    mysql.connection.commit()    
    data = cur.fetchone()
    cur.close()   
    return data

# This function selects common values between two tables
def join_tables(output, table1, table2, table1_column_name, table2_column_name):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s LEFT OUTER JOIN %s ON %s = %s" % (output, table1, table2, table1_column_name, table2_column_name))
    mysql.connection.commit()    
    data = cur.fetchall()
    cur.close()   
    return data

# This function selects common values from two tables
def common_values_not_unique(output, table1, common_column, table2, conditions): 
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s WHERE %s IN (SELECT %s FROM %s WHERE %s)" % (output, table1, common_column, common_column, table2, conditions))
    mysql.connection.commit()    
    data = cur.fetchall()
    cur.close()   
    return data

# This function only one common value from two tables
def common_value_not_unique(output, table1, common_column, table2, conditions): 
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s WHERE %s IN (SELECT %s FROM %s WHERE %s)" % (output, table1, common_column, common_column, table2, conditions))
    mysql.connection.commit()    
    data = cur.fetchone()
    cur.close()   
    return data

# This function selects entries from table1 that aren't in table 2
def compare_two_tables(output, table1, common_column, table2, conditions): 
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s WHERE %s NOT IN (SELECT %s FROM %s WHERE %s)" % (output, table1, common_column, common_column, table2, conditions))
    mysql.connection.commit()    
    data = cur.fetchall() #built in function to return a tuple, list or dictionary
    cur.close()   
    return data

def compare_two_tables2(table1, table2, common_column):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT * FROM %s WHERE NOT EXISTS (SELECT 1 FROM %s WHERE %s.%s = %s.%s)" % (table1, table2, table1, common_column, table2, common_column))
    mysql.connection.commit()    
    data = cur.fetchall() #built in function to return a tuple, list or dictionary
    cur.close()   
    return data

# This function selects entries from table1 that aren't in table 2
def compare_two_tables_new_quizzes(round_id): 
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT quizzes.quiz_id, quizzes.quiz_description, quizzes.quiz_name FROM quizzes LEFT OUTER JOIN live ON quizzes.quiz_id = live.quiz_id WHERE live.round_id IS NULL OR live.round_id != %s;" % (round_id))
    mysql.connection.commit()    
    data = cur.fetchall() #built in function to return a tuple, list or dictionary
    cur.close()   
    return data

def compare_two_tables_new_questions(round_id): 
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT questions.question_id, questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points, live.round_id FROM questions LEFT OUTER JOIN live ON questions.question_id = live.question_id WHERE live.round_id IS NULL OR live.round_id != %s;" % (round_id))
    mysql.connection.commit()    
    data = cur.fetchall() #built in function to return a tuple, list or dictionary
    cur.close()   
    return data


# def compare_two_tables_new_questions(): 
#     cur = mysql.connection.cursor(cursorclass=DictCursor)
#     cur.execute("SELECT questions.question_id, questions.question_tag, live.round_id FROM questions LEFT OUTER JOIN live ON questions.question_id = live.question_id")
#     mysql.connection.commit()    
#     data = cur.fetchall() #built in function to return a tuple, list or dictionary
#     cur.close()   
#     return data

# This function selects entries from table1 that aren't in table 2
def compare_two_tables_name(output, table1, foreign_key_column, referenced_column, table2, conditions): 
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s WHERE %s NOT IN (SELECT %s FROM %s WHERE %s)" % (output, table1, foreign_key_column, referenced_column, table2, conditions))
    mysql.connection.commit()    
    data = cur.fetchall() #built in function to return a tuple, list or dictionary
    cur.close()   
    return data

# This function deletes a table entry based on a condition
def delete_db_entry(table, conditions):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM %s WHERE %s" % (table, conditions))
    mysql.connection.commit()
    cur.close()

# This function returns outputs from a table based on the value.
def get_entries_from_db(output, table, conditions): 
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s WHERE %s" % (output, table, conditions))
    mysql.connection.commit()
    data = cur.fetchall() #built in function to return a tuple, list or dictiona
    cur.close()   
    return data # returns as a dict

# This function returns a single output from a table based on the value.
def get_entry_from_db(output, table, conditions):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT %s FROM %s WHERE %s" % (output, table, conditions))
    mysql.connection.commit()
    data = cur.fetchone() #built in function to return a tuple, list or dictionary
    cur.close()   
    return data # returns as a dict

# This function returns one or all the values based on a query
def get_values(amount, query):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute(query) # Query must already be in a string format
    mysql.connection.commit()
    if amount == "all":    
        data = cur.fetchall() #built in function to return a tuple, list or dictionary
    else:
        data = cur.fetchone() #built in function to return a tuple, list or dictionary
    cur.close() 
    return data

# This function will insert a value into a database
def insert_db_entry(table, columns, values):
    cur = mysql.connection.cursor()
    cur.execute("INSERT IGNORE INTO %s (%s) VALUES (%s)" % (table, columns, values))
    mysql.connection.commit()
    cur.close()

# Returns the AUTO_INCREMENT id of the last row that has been inserted or updated in a table
def get_latest():
    cur = mysql.connection.cursor()
    cur.execute("SELECT LAST_INSERT_ID()")
    mysql.connection.commit()
    data = cur.fetchone() #built in function to return a tuple, list or dictionary
    cur.close()
    return data

# This function will update a value in a table
# Initially was a list for updates and conditions, but string more efficient as no minipulation required
def update_db_entry(table, updates, conditions): 
    cur = mysql.connection.cursor()
    cur.execute("UPDATE %s SET %s WHERE %s" % (table, updates, conditions))
    mysql.connection.commit()
    cur.close() 


def remove_dictionary_duplicates(input_list, key):
    unique_list = []
    hash_table = {}
    name_hash_table = {}

    for dictionary in input_list:
        dictionary_key = tuple(dictionary.items())

        if dictionary_key not in hash_table:
            if dictionary[key] not in name_hash_table:
                unique_list.append(dictionary)
                name_hash_table[dictionary[key]] = True
                hash_table[dictionary_key] = dictionary

    return unique_list

def compare_dictionary_lists(input_list, exclude_list, key):
    question_id_set = set()
    removed = False

    while not removed:
        for item in exclude_list:
            question_id_set.add(item[key])

        removed = True

        for item in input_list:
            index = input_list.index(item)
            if index == (len(input_list) - 1):
                if item[key] in question_id_set:
                    input_list.remove(item)
                    removed = False
            else:
                if item[key] in question_id_set:
                    input_list.remove(item)
                    removed = False

    return input_list

def average(list_of_dicts, key):
    if not list_of_dicts:
        return 0

    total_value = 0
    for dict in list_of_dicts:
        if key not in dict:
            raise ValueError("The list of list_of_dicts does not contain the key %s." % (key))

        dict_value = dict.get(key, 0)
        if dict_value is not None:
            total_value += dict_value

    average_value = total_value / len(list_of_dicts)
    # average_value is a float e.g. 5.0, remove int to make it 100 scale
    return int(average_value)

def mode(data, key):
    counts = {}
    for item in data:
        value = item.get(key)
        if value is not None:
            if value in counts:
                counts[value] += 1
            else:
                counts[value] = 1

    # Check for modes and handle None values
    if len(counts) == 0:
        return []

    mode_values = []
    mode_counts = max(counts.values())
    for value, count in counts.items():
        if count == mode_counts and value is not None:
            mode_values.append(value)
    return mode_values or []


def total(list_of_dicts, key):
    total_value = 0
    for dict in list_of_dicts:
        try:
            if dict[key] is not None:
                total_value += dict[key]
        except KeyError:
            pass

    return total_value


def mark_answer(question_id, round_id, quiz_id):
    question_info = get_entry_from_db(
        "question_scoring_type_id, question_points",
        "questions",
        "question_id = " + str(question_id)
    )

    answer_info = get_entries_from_db(
        "*",
        "answers",
        "answer_correct = 1 AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (question_id, round_id, quiz_id)
    )

    # Order answers by time answered
    answer_info = sorted(answer_info, key=lambda k: k['answer_timestamp'])
    # Set incorrect answer points to 0
    update_db_entry(
        "answers",
        "answer_points = 0",
        "answer_correct = 0 AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (question_id, round_id, quiz_id)
    )

    # Fastest Finger
    if question_info['question_scoring_type_id'] == 1:
        points = question_info['question_points']
        for i in range(len(answer_info)):
            if points > 0:
                update_db_entry(
                    "answers",
                    "answer_points = %s" % (points),
                    "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (answer_info[i]['user_id'], answer_info[i]['question_id'], answer_info[i]['round_id'], answer_info[i]['quiz_id'])
                )
                points -= 1  # Decrement points for the next dictionary
            else:
                break  # Stop adding points if we reach 0
    
    # Right or Wrong
    elif question_info['question_scoring_type_id'] == 2:
        for answer in answer_info:
            update_db_entry(
                "answers",
                "answer_points = %s" % (question_info['question_points']),
                "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (answer['user_id'], answer['question_id'], answer['round_id'], answer['quiz_id'])
            )
        
def update_leaderboard(user_id, quiz_id, points):
    if check_single_db(
        "participant_score",
        "participants",
        "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
    ):
        # Find current user score in quiz
        participant_score = get_entry_from_db(
            "participant_score",
            "participants",
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
        )['participant_score']
    
    else:
        participant_score = 0

    # Adds/Subtracts new points to exisiting score
    update_db_entry(
        "participants",
        "participant_score = %s" % (int(participant_score)+int(points)),
        "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
    )

    # Gets all the scores from the quiz
    participant_info = get_entries_from_db(
        "participant_score, user_id",
        "participants",
        "quiz_id = %s" % (quiz_id)
    )

    # Sorts the user id's based on score
    participant_info = sorted(participant_info, key=lambda k: -k['participant_score'])

    # Cycle through all participants and update position
    current_position = 1
    previous_score = None
    for participant in participant_info:
        if participant["participant_score"] != previous_score:
            current_position = participant_info.index(participant) + 1  # Use data.index to get position in original list
        # participant["participant_position"] = current_position
        update_db_entry(
            "participants",
            "participant_position = %s" % (current_position),
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (participant["user_id"], quiz_id)
        )
        previous_score = participant["participant_score"]

def fix_string(text):
    text = text.replace('\\', '')
    text = text.replace('"', '\\"')
    text = text.replace("'", "\\'")
    return text

def filter_data(data, user_id):
    target_position = next((d['participant_position'] for d in data if d['user_id'] == user_id), None)
    filtered_data = []

    if target_position is None:
        return filtered_data  # Handle case where user_id doesn't exist

    # Find next greater position (if it exists)
    next_greater = min((p for p in [d['participant_position'] for d in data] if p > target_position), default=None)

    # Handle case where target_position is 1 (no lesser value)
    if target_position == 1:
        next_lesser = None
    # Handle case where target_position is the highest value (no greater value)
    elif next_greater is None:
        next_lesser = max(p for p in [d['participant_position'] for d in data] if p < target_position)
    else:
        next_lesser = max(p for p in [d['participant_position'] for d in data] if p < target_position)

    # Add dictionaries with matching positions
    filtered_data.extend(
        d for d in data if d['participant_position'] in (target_position, next_greater, next_lesser, 1)
    )

    return filtered_data

def filter_data_old(data, user_id):
    target_position = next(d['participant_position'] for d in data if d['user_id'] == user_id)
    filtered_data = [d for d in data if d['participant_position'] in (target_position + 1, target_position - 1, target_position)]

    # Ensure at least one dictionary with position 1 is included
    if not any(d['participant_position'] == 1 for d in filtered_data):
        filtered_data.extend([d for d in data if d['participant_position'] == 1])

    return filtered_data

def get_item(user_id, quiz_id):
    position = get_entry_from_db(
        "participant_position",
        "participants",
        "user_id = %s" % (user_id)
    )['participant_position']

    number_of_participants = len(get_entries_from_db(
        "user_id",
        "participants",
        "quiz_id = %s" % (quiz_id)
    ))

    items = get_entries_from_db(
        "item_id, item_rarity",
        "items",
        "item_id IS NOT NULL"
    )

    if random.random()+(position/number_of_participants) > 1:
        options = []
        for item in items:
            options = options + [item['item_id']]*int(item['item_rarity']*(position/number_of_participants))
        item = random.choice(options)
        update_db_entry(
            "participants",
            "participant_item_id = %s" % (item),
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
        )

def item_function(user_id, quiz_id, participant_item_id, use):
    item_info = get_entry_from_db(
        "*",
        "items",
        "item_id = %s" % (participant_item_id)
    )

    # Banana
    if item_info['item_id'] == 1:
        # Thrown Forwards
        if int(use) == 1:
            if check_success(item_info['chance_forwards']):
                user_position = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
                )['participant_position']

                someone_else_in_first = check_single_db(
                    "participant_position",
                    "participants",
                    "user_id != \"%s\" AND quiz_id = \"%s\" AND participant_position = \"1\"" % (user_id, quiz_id)
                )

                if user_position == 1 and not someone_else_in_first:
                    flash("You threw the %s forwards into the abyss" % (item_info['item_name']))
                else:
                    user = common_value(
                        "users.username, participants.user_id, participants.participant_position",
                        "users",
                        "participants",
                        "users.user_id",
                        "participants.user_id WHERE participant_position <= \"%s\" AND participants.user_id != \"%s\" AND quiz_id = \"%s\" ORDER BY participant_position DESC LIMIT 1" % (user_position, user_id, quiz_id)
                    )

                    update_leaderboard(user['user_id'], quiz_id, item_info['item_points'])
                    flash("You threw a %s forwards and it hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(item_info['item_points'])))
            else:
                flash("You threw a %s forwards but it missed." % (item_info['item_name']))

        # Thrown Backwards
        if int(use) == 2:
            if check_success(item_info['chance_backwards']):
                user_position = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
                )['participant_position']

                last_place = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "quiz_id = \"%s\" AND participant_position = (SELECT MAX(participant_position) FROM participants)" % (quiz_id)
                )['participant_position']

                someone_else_in_last = check_single_db(
                    "participant_position",
                    "participants",
                    "user_id != \"%s\" AND quiz_id = \"%s\" AND participant_position = \"%s\"" % (user_id, quiz_id, last_place)
                )

                if user_position == last_place and not someone_else_in_last:
                    flash("You threw the %s backwards into the abyss" % (item_info['item_name']))
                else:
                    user = common_value(
                        "users.username, participants.user_id, participants.participant_position",
                        "users",
                        "participants",
                        "users.user_id",
                        "participants.user_id WHERE participant_position >= \"%s\" AND participants.user_id != \"%s\" AND quiz_id = \"%s\" ORDER BY participant_position ASC LIMIT 1" % (user_position, user_id, quiz_id)
                    )

                    update_leaderboard(user['user_id'], quiz_id, item_info['item_points'])
                    flash("You threw a %s backwards and it hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(item_info['item_points'])))
            else:
                flash("You threw a %s backwards but it missed." % (item_info['item_name']))

    # Green Shell
    if item_info['item_id']  == 2:
        # Thrown Forwards
        if int(use) == 1:
            if check_success(item_info['chance_forwards']):
                user_position = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
                )['participant_position']

                someone_else_in_first = check_single_db(
                    "participant_position",
                    "participants",
                    "user_id != \"%s\" AND quiz_id = \"%s\" AND participant_position = \"1\"" % (user_id, quiz_id)
                )

                if user_position == 1 and not someone_else_in_first:
                    flash("You threw the %s forwards into the abyss" % (item_info['item_name']))
                else:
                    user = common_value(
                        "users.username, participants.user_id, participants.participant_position",
                        "users",
                        "participants",
                        "users.user_id",
                        "participants.user_id WHERE participant_position <= \"%s\" AND participants.user_id != \"%s\" AND quiz_id = \"%s\" ORDER BY participant_position DESC LIMIT 1" % (user_position, user_id, quiz_id)
                    )

                    update_leaderboard(user['user_id'], quiz_id, item_info['item_points'])
                    flash("You threw a %s forwards and it hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(item_info['item_points'])))
            else:
                flash("You threw a %s forwards but it missed." % (item_info['item_name']))

        # Thrown Backwards
        if int(use) == 2:
            if check_success(item_info['chance_backwards']):
                user_position = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
                )['participant_position']

                last_place = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "quiz_id = \"%s\" AND participant_position = (SELECT MAX(participant_position) FROM participants)" % (quiz_id)
                )['participant_position']

                someone_else_in_last = check_single_db(
                    "participant_position",
                    "participants",
                    "user_id != \"%s\" AND quiz_id = \"%s\" AND participant_position = \"%s\"" % (user_id, quiz_id, last_place)
                )

                if user_position == last_place and not someone_else_in_last:
                    flash("You threw the %s backwards into the abyss" % (item_info['item_name']))
                else:
                    user = common_value(
                        "users.username, participants.user_id, participants.participant_position",
                        "users",
                        "participants",
                        "users.user_id",
                        "participants.user_id WHERE participant_position >= \"%s\" AND participants.user_id != \"%s\" AND quiz_id = \"%s\" ORDER BY participant_position ASC LIMIT 1" % (user_position, user_id, quiz_id)
                    )

                    update_leaderboard(user['user_id'], quiz_id, item_info['item_points'])
                    flash("You threw a %s backwards and it hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(item_info['item_points'])))
            else:
                flash("You threw a %s backwards but it missed." % (item_info['item_name']))

    # Red Shell
    if item_info['item_id']  == 3:
        # Thrown Forwards
        if int(use) == 1:
            user_position = get_entry_from_db(
                "participant_position",
                "participants",
                "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
            )['participant_position']

            someone_else_in_first = check_single_db(
                "participant_position",
                "participants",
                "user_id != \"%s\" AND quiz_id = \"%s\" AND participant_position = \"1\"" % (user_id, quiz_id)
            )

            if user_position == 1 and not someone_else_in_first:
                flash("You threw the %s forwards into the abyss" % (item_info['item_name']))
            else:
                user = common_value(
                    "users.username, participants.user_id, participants.participant_position",
                    "users",
                    "participants",
                    "users.user_id",
                    "participants.user_id WHERE participant_position <= \"%s\" AND participants.user_id != \"%s\" AND quiz_id = \"%s\" ORDER BY participant_position DESC LIMIT 1" % (user_position, user_id, quiz_id)
                )

                update_leaderboard(user['user_id'], quiz_id, item_info['item_points'])
                flash("You threw a %s forwards and it hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(item_info['item_points'])))

        # Thrown Backwards
        if int(use) == 2:
            if check_success(item_info['chance_backwards']):
                user_position = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
                )['participant_position']

                last_place = get_entry_from_db(
                    "participant_position",
                    "participants",
                    "quiz_id = \"%s\" AND participant_position = (SELECT MAX(participant_position) FROM participants)" % (quiz_id)
                )['participant_position']

                someone_else_in_last = check_single_db(
                    "participant_position",
                    "participants",
                    "user_id != \"%s\" AND quiz_id = \"%s\" AND participant_position = \"%s\"" % (user_id, quiz_id, last_place)
                )

                if user_position == last_place and not someone_else_in_last:
                    flash("You threw the %s backwards into the abyss" % (item_info['item_name']))
                else:
                    user = common_value(
                        "users.username, participants.user_id, participants.participant_position",
                        "users",
                        "participants",
                        "users.user_id",
                        "participants.user_id WHERE participant_position >= \"%s\" AND participants.user_id != \"%s\" AND quiz_id = \"%s\" ORDER BY participant_position ASC LIMIT 1" % (user_position, user_id, quiz_id)
                    )

                    update_leaderboard(user['user_id'], quiz_id, item_info['item_points'])
                    flash("You threw a %s backwards and it hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(item_info['item_points'])))
            else:
                flash("You threw a %s backwards but it missed." % (item_info['item_name']))
   
    # Lightning
    if item_info['item_id']  == 4:
        # Thrown Forwards
        user_position = get_entry_from_db(
            "participant_position",
            "participants",
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
        )['participant_position']

        users = common_values(
            "users.username, participants.user_id, participants.participant_position",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE users.user_id != \"%s\" AND participants.participant_position <= \"%s\" AND participants.quiz_id = \"%s\"" % (user_id, user_position, quiz_id)
        )

        for user in users:
            update_leaderboard(user['user_id'], quiz_id, item_info['item_points'])
            flash("You used a %s and hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(item_info['item_points'])))

    # Blue Shell
    if item_info['item_id']  == 5:
        # Thrown Forwards
        damage = {"1": item_info['item_points']}
        points = abs(item_info['item_points'])
        index = 0
        while points > 0:  # Limit to 100 iterations to avoid infinite loops
            halved_value = points // 2
            if halved_value != 0:
                damage[str(int(index+2))] = -halved_value
            points = halved_value
            index += 1 

        targets = []
        for key in damage.keys():
            users = common_values(
                "users.username, participants.user_id, participants.participant_position",
                "users",
                "participants",
                "users.user_id",
                "participants.user_id WHERE users.user_id != \"%s\" AND participants.participant_position = \"%s\" AND participants.quiz_id = \"%s\"" % (user_id, key, quiz_id)
            )
            targets.extend(users)

        for user in targets:
            for key, value in damage.items():
                if int(user['participant_position']) == int(key):
                    update_leaderboard(user['user_id'], quiz_id, value)
                    flash("You used a %s and hit %s in %s place, taking %s points" % (item_info['item_name'], user['username'], ordinal(int(user['participant_position'])), abs(value)))



    # 1up Mushroom
    if item_info['item_id']  == 6:
        # Use on self
        user_info = get_entry_from_db(
            "participant_position, participant_score",
            "participants",
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
        )
        
        user_position = user_info['participant_position']
        user_score = user_info['participant_score']

        if user_position == 1:
            flash("There's nowhere for you to go, you're already winning")
        else:
            next_participant_info = get_entry_from_db(
                "participant_score, participant_position",
                "participants",
                "participant_position < \"%s\" AND quiz_id = \"%s\" ORDER BY participant_position DESC LIMIT 1" % (user_position, quiz_id)
            )

            next_score = next_participant_info['participant_score']
            new_position = next_participant_info['participant_position']

            points = next_score - user_score + 1

            update_leaderboard(user_id, quiz_id, points)
            flash("You used a %s to gain %s points and moved to %s place" % (item_info['item_name'], points, ordinal(int(new_position))))

    # Coin
    if item_info['item_id']  == 7:
        # Use on self
        update_leaderboard(user_id, quiz_id, item_info['item_points'])
        flash("You used a %s and gained %s points" % (item_info['item_name'], item_info['item_points']))

    # Red Mushroom
    if item_info['item_id']  == 8:
        # Use on self
        update_leaderboard(user_id, quiz_id, item_info['item_points'])
        flash("You used a %s and gained %s points" % (item_info['item_name'], item_info['item_points']))
    
    # Golden Mushroom
    if item_info['item_id']  == 9:
        # Use on self
        update_leaderboard(user_id, quiz_id, item_info['item_points'])
        flash("You used a %s and gained %s points" % (item_info['item_name'], item_info['item_points']))

    # Golden Pipe
    if item_info['item_id']  == 10:
        # Use on self
        user_position = get_entry_from_db(
            "participant_position",
            "participants",
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
        )['participant_position']

        if user_position == 1:
            flash("You can't use the %s. There's nowhere for you to go, you're already winning" % (item_info['item_name']))
        else:
            first_place_score = get_entry_from_db(
                "participant_score",
                "participants",
                "participant_position = \"1\" AND quiz_id = \"%s\"" % (quiz_id)
            )['participant_score']

            user_score = get_entry_from_db(
                "participant_score",
                "participants",
                "user_id = \"%s\" AND quiz_id = \"%s\"" % (user_id, quiz_id)
            )['participant_score']

            points = first_place_score - user_score + 1

            update_leaderboard(user_id, quiz_id, points)

            flash("You used a %s and went straight to 1st place!" % (item_info['item_name']))

def ordinal(num):
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    suffix = suffixes.get(num % 10, 'th')  # Default to 'th' for most cases

    # Handle exceptions for 11, 12, and 13:
    if 11 <= (num % 100) <= 13:
        suffix = 'th'

    return f"{num}{suffix}"
  
def check_success(chance):
    if chance <= 0 or chance >= 100:
        raise ValueError("chance_forwards must be between 0 and 100")

    random_number = random.random()*100  # Generate a random number between 1 and 100
    if random_number <= chance:
        return True
    else:
        return False
    
def detect_urls(text):
    url_regex = r"https?://[^\s<>]+|www\.[^\s<>]+" 
    matches = re.findall(url_regex, text)  # Find all URLs
    urls = matches  # Store URLs for separate use

    # Remove URLs from the text
    clean_text = re.sub(url_regex, "", text)

    return clean_text, urls