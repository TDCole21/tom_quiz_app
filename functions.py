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
    return re.search("@", test_string)

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
        raise ValueError("The list of list_of_dicts is empty.")

    total_value = 0
    for dict in list_of_dicts:
        if key not in dict:
            raise ValueError("The list of list_of_dicts does not contain the key " + key + ".")

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
    if not list_of_dicts:
        raise ValueError("The list of list_of_dicts is empty.")

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
        "answer_correct = 1 AND question_id = \""+ str(question_id) + "\" AND round_id = \"" + str(round_id) + "\" AND quiz_id = \"" + str(quiz_id) + "\""
    )

    # Order answers by time answered
    answer_info = sorted(answer_info, key=lambda k: k['answer_timestamp'])
    # Set incorrect answer points to 0
    update_db_entry(
        "answers",
        "answer_points = 0",
        "answer_correct = 0 AND question_id = \""+ str(question_id) + "\" AND round_id = \"" + str(round_id) + "\" AND quiz_id = \"" + str(quiz_id) + "\""
    )

    # Fastest Finger
    if question_info['question_scoring_type_id'] == 1:
        points = question_info['question_points']
        for i in range(len(answer_info)):
            if points > 0:
                update_db_entry(
                    "answers",
                    "answer_points = " + str(points),
                    "user_id = \"" + str(answer_info[i]['user_id']) + "\" AND question_id = \"" + str(answer_info[i]['question_id']) + "\" AND round_id = \"" + str(answer_info[i]['round_id']) + "\" AND quiz_id = \"" + str(answer_info[i]['quiz_id']) + "\""
                )
                points -= 1  # Decrement points for the next dictionary
            else:
                break  # Stop adding points if we reach 0