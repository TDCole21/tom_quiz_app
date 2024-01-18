from functions import *

######################################################################################################################################################################
# HOME
######################################################################################################################################################################

# Template login page
@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    return render_template(
        "misc/index.html",
        info = session,
        name = "Home"
    )


######################################################################################################################################################################
# LOGIN
######################################################################################################################################################################

# If you are not currently logged in, it directs you to the login html page, otherwise it redirects you to the profile page.
@app.route('/login')
def login_page():       
    if not 'loggedin' in session:      
        return render_template(
            "users/login.html",
            name = "Login"
        )

    else:
        return redirect(url_for(
            'profile'
        ))

# From the login page, this function will take the user information, check it against a database, and if it exists, then will login the user into the session
@app.route('/login/submit', methods=['GET', 'POST'])
def login_attempt():
    if request.method == 'POST':
        # Checking if user has tried to login using an email or username
        if email(fix_string(request.form.get('user_details'))):
            login_via = "user_email"

        else:
            login_via = "username"

        # Checks if the username or Email exists in the users database
        if check_single_db(
            "user_id",
            "users",
            "%s = \"%s\"" % (login_via, fix_string(request.form.get('user_details')))
        ):
            # Checks if the input password, when hashed, matches the one on the database
            if check_password_hash(
                get_entry_from_db(
                    "user_password",
                    "users",
                    "%s = \"%s\"" % (login_via, fix_string(request.form.get('user_details')))
                )['user_password'],
                fix_string(request.form.get('user_password'))
            ):
                # Get user information
                account = get_entry_from_db(
                    "user_id, username, user_email, user_admin",
                    "users",
                    "%s = \"%s\"" % (login_via, fix_string(request.form.get('user_details')))
                )

                # Enters user information in the session
                login_session(
                    account["user_id"],
                    account["username"],
                    account["user_email"],
                    account["user_admin"]
                )

                # Login is successful, so redirect user to the profile page
                return redirect(url_for(
                    'profile'
                ))
            
            # User exists, but password is wrong. Login failed
            else:
                flash('Please check your login details and try again.')
        
        # username/User Email does not exist in the database
        else:
            flash('This account does not exist.')

    # If no post method was used, or the user was failed to login, then they're redirected to the login page 
    return redirect(url_for(
        'login_page'
    ))

# This is accessed via the nav-bar and logs the user out of the sesion
@app.route('/logout')
def logout_user():   
    # Logs user out of the current session      
    logout_session()
    flash('You have successfully logged out')   
    # Redirects user to login page
    return redirect(url_for(
        'login_page'
    ))

# This is accesed via the nav-bar and takes the user to the forgot password html page
@app.route('/forgot_password')
def forgot_password():   
    # Redirects to forgot password html page
    flash('This page is not finished')
    return render_template(
        "users/forgot_password.html",
        name = "Forgot Password"
    )


######################################################################################################################################################################
# USERS
######################################################################################################################################################################

# Profile login page
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # Redirects to profile page with user information from session
        # Is the email needed here?
        return render_template(
            "users/profile.html",
            username = session['username'],
            email = session['user_email'],
            name = "Profile"
        )
    # User is not loggedin redirect to login page
    return redirect(url_for(
        'login_page'
    ))

# Deletes the user from the database
@app.route('/profile/delete', methods=['GET', 'POST'])
def profile_delete():
    if request.method == "POST":
        # Deletes user from the database based on the username
        delete_db_entry(
            "users",
            "username = \"%s\"" % (session['username'])
        )
        # Logs the user out of the session
        logout_session()
        flash('You have successfully deleted your account')     

        # Redirects user to home page
        return redirect(url_for(
            'home'
        ))
    
    # Redirects user to home page, with non-user message
    flash('Naughty naughty, you need an account to do that')   
    return redirect(url_for(
        'home'
    ))

# Updates the user's email in the database and session
@app.route('/profile/email/update', methods=['GET', 'POST'])
def email_update():
    if request.method == "POST":
        # Checks if the requested email already exists in the database
        if check_single_db(
            "user_id",
            "users",
            "user_email = \"%s\"" % (fix_string(request.form.get('new_user_email')))
        ):
            flash('That email is already in use.')

        else:
            # Updates the database entry with the new email address
            update_db_entry(
                "users",
                "user_email = \"%s\"" % (fix_string(request.form.get('new_user_email'))),
                "user_email = \"%s\"" % (session['user_email'])
            )
            # Updates the session with the new email address
            session['user_email'] = fix_string(request.form.get('new_user_email'))

    # Redirects back to the profile page
    return redirect(url_for(
        'profile'
    ))

# Updates the user's username in the database and session
@app.route('/profile/username/update', methods=['GET', 'POST'])
def username_update():
    if request.method == "POST":
        # Checks is the username contains an @ symbol. I use the @ symbol to differentiate between user email and username
        if email(fix_string(request.form.get('new_username'))):
            flash('A username cannot contain an @ character.')

        # Checks if the new username already exists in the database
        elif check_single_db(
            "user_id",
            "users",
            "username = \"%s\"" % (fix_string(request.form.get('new_username')))
        ):
            flash('That username is already in use.')

        else:
            # Updates the username entry in the database with the new username, using the session email as the identifier
            update_db_entry(
                "users",
                "username = \"%s\"" % (fix_string(request.form.get('new_username'))),
                "username = \"%s\"" % (session['username'])
            )
            # Updates the session with the new username
            session['username'] = fix_string(request.form.get('new_username'))

    # Redirects user to profile page
    return redirect(url_for(
        'profile'
    ))

# Updates the user's password in the database
@app.route('/profile/password/update', methods=['GET', 'POST'])
def password_update():
    if request.method == "POST":
        # Updates the user's password in the database, using the session email as the identifier
        update_db_entry(
            "users",
            "user_password = \"%s\"" % (generate_password_hash(fix_string(request.form.get('new_user_password')), method='SHA1')),
            "user_email = \"%s\"" % (session['user_email'])
        )

    # Redirects user to the profile page
    return redirect(url_for(
        'profile'
    ))


######################################################################################################################################################################
# REGISTER
######################################################################################################################################################################

# Create account template page
@app.route('/register')
def register():
    # Checks if the person accessing the url link is logged into the session
    if not 'loggedin' in session:
        # If not logged in, redirects user to the register page
        return render_template(
            "users/register.html",
            name = "Register"
        )

    else:
        # If the user is already logged in, then they are redirected to their profile page
        return redirect(url_for(
            'profile'
        ))

# This creates a new entry into the users table in the database, using the information submitted via the form by the user
@app.route('/register/submit', methods=['GET', 'POST'])
def user_create():
    if request.method == "POST":
        # Checks if the username has an @ character. My backend differentiates emails and usernames based on this
        if email(fix_string(request.form.get('username'))):
            flash('Signup failed. A username cannot contain an @ character.')

        # Checks is the username or email already exists in the database
        elif check_single_db(
            "user_id",
            "users",
            "username = \"%s\" OR user_email = \"%s\"" % (fix_string(request.form.get('username')), fix_string(request.form.get('user_email')))
        ):
            flash('That account is already in use.')
            flash('login')

        else:
            # checks if the password and repeat password are the same
            if duplicate(
                fix_string(request.form.get('user_password')),
                fix_string(request.form.get('user_password_repeat'))
            ):
                # Inserts the new values into the users table in the database. By default the user is not an admin (admin=0)
                insert_db_entry(
                    "users",
                    "username, user_email, user_password, user_admin",
                    "\"%s\", \"%s\", \"%s\", 0" % (fix_string(request.form.get('username')), fix_string(request.form.get('user_email')), generate_password_hash(fix_string(request.form.get('user_password')), method='SHA1'))
                )

                # This then grabs the information that was just entered into the database
                account = get_entry_from_db(
                    "user_id, username, user_email, user_admin",
                    "users",
                    "user_email = \"%s\"" % (fix_string(request.form.get('user_email')))
                )
                
                # Logs the user into the session
                login_session(
                    account["user_id"],
                    account["username"],
                    account["user_email"],
                    account["user_admin"]
                )
                # Redirects the user to their profile page
                return redirect(url_for(
                    'profile'
                ))

            # If the user failed the password repetition
            else:
                flash('Signup failed. Passwords were different.')
                # potentially include a return that will keep the name   
                
    # If the user nativgated to the url without a post method, or failed to create an account, they're redirected to the register page                   
    return redirect(url_for(
        'register'
    ))


######################################################################################################################################################################
# QUIZ
######################################################################################################################################################################

# HTML template for the quizzes (to host, join or make/edit)
@app.route('/quiz')
def quiz():
    return render_template(
        "quiz/quiz.html",
        name = "Quiz"
    )

# QUIZ MANAGER (MAKE/EDIT)     ############################################################################

# HTML template for quiz maker/editor page. The page will display info on all quizes. The page will redirect those who aren't admins.
@app.route('/quiz_manager', methods=['GET', 'POST'])
def quiz_manager():
    # Check to see if the user is an admin
    if admin_check():
        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/quiz_manager.html",
            name = "Quiz Manager",
        )
    
    else:
        return redirect(url_for(
            'home'
        ))  
    
# QUIZ #

@app.route('/quiz_maker', methods=['GET', 'POST'])
def quiz_maker():
    # Check to see if the user is an admin
    if admin_check():
        # Gets all quizzes from the quiz table
        quiz_info = join_tables(
            "DISTINCT quizzes.quiz_id, quizzes.quiz_description, quizzes.quiz_name, live.quiz_active, live.quiz_completed",
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE quizzes.quiz_id IS NOT NULL"
        )

        for quiz in quiz_info:
            associated_rounds = []
            # Collects information on all the quizzes this round is associated with
            associated_round_info = common_values(
                "rounds.round_name, rounds.round_id",
                "rounds",
                "live",
                "rounds.round_id",
                "live.round_id WHERE live.quiz_id = %s" % (quiz['quiz_id'])
            )
            for associated_round in associated_round_info:
                associated_rounds.append(associated_round['round_name'])

            quiz['number_of_associated_rounds'] = len(associated_rounds)
            quiz['associated_rounds'] = " and ".join(associated_rounds)

            associated_questions = []
            for round in associated_round_info:
                # Collects information on all the quizzes this round is associated with
                associated_question_info = common_values(
                    "questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points",
                    "questions",
                    "live",
                    "questions.question_id",
                    "live.question_id WHERE live.round_id = %s" % (round['round_id'])
                )
                for associated_question in associated_question_info:
                    associated_questions.append(associated_question['question_tag'])

            # associated_questions = set(associated_questions)
            quiz['associated_questions'] = " and ".join(associated_questions)
            quiz['number_of_associated_questions'] = len(associated_questions)

            if associated_questions:
                # Average question difficulty
                quiz['average_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                quiz['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    quiz['mode_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        quiz['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        quiz['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        quiz['mode_category'] = "Not set"


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/quizzes/quiz_maker.html",
            name                    = "Quiz Maker",
            quiz_info               = quiz_info
        )
    
    else:
        return redirect(url_for(
            'home'
        )) 

# Creates a basic entry into the quiz table, using only the quiz Name
@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    # Check to see if the user is an admin, and redirects to the home page if not
    if admin_check() and request.method == "POST":
        # Checks if a quiz already has the name
        if check_single_db(
            "quiz_id",
            "quizzes",
            "quiz_name = \"%s\"" % (fix_string(request.form.get('quiz_name')))
        ):
            # Redirects user to the quiz maker/editor page
            flash('The quiz name, \"%s\", is already in use.' % (request.form.get('quiz_name')))
            return redirect(url_for(
                'quiz_maker'
            ))

        else:
            # Creates a new entry in the quiz table using the quiz name form the form
            insert_db_entry(
                "quizzes",
                "quiz_name",
                "\"%s\"" % (fix_string(request.form.get('quiz_name')))
            )

            # Redirects user to the quiz template page for the newly created quiz
            flash('The Quiz, \"%s\", was successfully created.' % (request.form.get('quiz_name')))
            return redirect(url_for(
                'quiz_maker'
            ))
    
    else:
        return redirect(url_for(
            'home'
        )) 

# This will remove a quiz from the database
@app.route('/delete_quiz', methods=['GET', 'POST'])
def delete_quiz():
    # Check to see if the user is an admin
    if admin_check() and request.method == "POST":
        # Checks to see if the quiz exists
        if not check_single_db(
            "quiz_id",
            "quizzes",
            "quiz_id = %s" % (request.form.get('quiz_id'))
        ):
            flash("This quiz does not exist")
            return redirect(url_for(
                'home'
            ))

        else:
            # Removes the quiz from the database based off the quiz_id
            delete_db_entry(
                "quizzes",
                "quiz_id = %s" % (request.form.get('quiz_id'))
            )

            # Redirects the user to the quiz Maker/Editor page
            flash ("The Quiz, \"%s\", has been deleted" % (request.form.get('quiz_name')))
            return redirect(url_for(
                'quiz_maker'
            ))
    
    else:
        return redirect(url_for(
            'home'
        ))

# Items

@app.route('/item_maker', methods=['GET', 'POST'])
def item_maker():
    # Check to see if the user is an admin
    if admin_check():
        # Gets all quizzes from the quiz table
        items = get_entries_from_db(
            "*",
            "items",
            "item_id IS NOT NULL"
        )


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/other/item_maker.html",
            name    = "Item Maker",
            items   = items
        )
    
    else:
        return redirect(url_for(
            'home'
        ))
    
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == "POST":
        if (request.form.get('item_rarity')):
            item_rarity = "\"%s\"" % (request.form.get('item_rarity'))
        else:
            item_rarity = "NULL"

        if (request.form.get('chance_forwards')):
            chance_forwards = "\"%s\"" % (request.form.get('chance_forwards'))
        else:
            chance_forwards = "NULL"

        if (request.form.get('chance_backwards')):
            chance_backwards = "\"%s\"" % (request.form.get('chance_backwards'))
        else:
            chance_backwards = "NULL"

        if (request.form.get('chance_use')):
            chance_use = "\"%s\"" % (request.form.get('chance_use'))
        else:
            chance_use = "NULL"

        if (request.form.get('item_points')):
            item_points = "\"%s\"" % (request.form.get('item_points'))
        else:
            item_points = "NULL"

        insert_db_entry(
            "items",
            "item_name, item_description, item_rarity, chance_forwards, chance_backwards, chance_use, item_points",
            "\"%s\", \"%s\", %s, %s, %s, %s, %s" % (fix_string(request.form.get('new_item_name')), fix_string(request.form.get('new_item_description')), item_rarity, chance_forwards, chance_backwards, chance_use, item_points),
        )

        flash("Item %s created" % (request.form.get('item_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/update_item', methods=['GET', 'POST'])
def update_item():
    if request.method == "POST":
        if (request.form.get('item_rarity')):
            item_rarity = "\"%s\"" % (request.form.get('item_rarity'))
        else:
            item_rarity = "NULL"

        if (request.form.get('chance_forwards')):
            chance_forwards = "\"%s\"" % (request.form.get('chance_forwards'))
        else:
            chance_forwards = "NULL"

        if (request.form.get('chance_backwards')):
            chance_backwards = "\"%s\"" % (request.form.get('chance_backwards'))
        else:
            chance_backwards = "NULL"

        if (request.form.get('chance_use')):
            chance_use = "\"%s\"" % (request.form.get('chance_use'))
        else:
            chance_use = "NULL"

        if (request.form.get('item_points')):
            item_points = "\"%s\"" % (request.form.get('item_points'))
        else:
            item_points = "NULL"

        update_db_entry(
            "items",
            "item_name = \"%s\", item_description = \"%s\", item_rarity = %s, chance_forwards = %s, chance_backwards = %s, chance_use = %s, item_points = %s" % (fix_string(request.form.get('new_item_name')), fix_string(request.form.get('new_item_description')), item_rarity, chance_forwards, chance_backwards, chance_use, item_points),
            "item_id = \"%s\"" % (fix_string(request.form.get('item_id')))
        )

        flash("Item %s updated" % (request.form.get('new_item_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    
@app.route('/delete_item', methods=['GET', 'POST'])
def delete_item():
    if request.method == "POST":
        update_db_entry(
            "participants",
            "participant_item_id = NULL",
            "participant_item_id = \"%s\"" % (request.form.get('item_id'))
        )
        delete_db_entry(
            "items",
            "item_id = \"%s\"" % (request.form.get('item_id'))
        )
        flash("Item %s deleted" % (request.form.get('item_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

# Categories

@app.route('/category_maker', methods=['GET', 'POST'])
def category_maker():
    # Check to see if the user is an admin
    if admin_check():
        # Gets all Categories
        categories = get_entries_from_db(
            "*",
            "categories",
            "category_id IS NOT NULL"
        )

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/other/category_maker.html",
            name                    = "Category Maker",
            categories              = categories
        )
    
    else:
        return redirect(url_for(
            'home'
        )) 

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == "POST":
        insert_db_entry(
            "categories",
            "category_name, category_description",
            "\"%s\", \"%s\"" % (fix_string(request.form.get('category_name')), fix_string(request.form.get('category_description')))
        )
        flash("Category %s created" % (request.form.get('category_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/update_category', methods=['GET', 'POST'])
def update_category():
    if request.method == "POST":
        update_db_entry(
            "categories",
            "category_name = \"%s\", category_description = \"%s\" " % (fix_string(request.form.get('new_category_name')), fix_string(request.form.get('new_category_description'))),
            "category_id = \"%s\"" % (request.form.get('category_id'))
        )
        flash("Category %s updated to %s" % (request.form.get('old_category_name'), request.form.get('new_category_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    
@app.route('/delete_category', methods=['GET', 'POST'])
def delete_category():
    if request.method == "POST":
        update_db_entry(
            "questions",
            "question_category_id = NULL",
            "question_category_id = \"%s\"" % (request.form.get('category_id'))
        )
        delete_db_entry(
            "categories",
            "category_id = \"%s\"" % (request.form.get('category_id'))
        )
        flash("Category %s deleted" % (request.form.get('category_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    
# Question Type

@app.route('/question_type_maker', methods=['GET', 'POST'])
def question_type_maker():
    # Check to see if the user is an admin
    if admin_check():
        # Gets all question types
        question_types = get_entries_from_db(
            "*",
            "question_type",
            "question_type_id IS NOT NULL"
        )

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/other/question_type_maker.html",
            name                    = "Question Type Maker",
            question_types          = question_types
        )
    
    else:
        return redirect(url_for(
            'home'
        )) 

@app.route('/add_question_type', methods=['GET', 'POST'])
def add_question_type():
    if request.method == "POST":
        insert_db_entry(
            "question_type",
            "question_type_name, question_type_description",
            "\"%s\", \"%s\"" % (fix_string(request.form.get('question_type_name')), fix_string(request.form.get('question_type_description')))
        )
        flash("Question type %s created" % (request.form.get('question_type_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/update_question_type', methods=['GET', 'POST'])
def update_question_type():
    if request.method == "POST":
        update_db_entry(
            "question_type",
            "question_type_name = \"%s\", question_type_description = \"%s\"" % (fix_string(request.form.get('new_question_type_name')), fix_string(request.form.get('new_question_type_description'))),
            "question_type_id = \"%s\"" % (request.form.get('question_type_id'))
        )
        flash("Question type %s updated to %s" % (request.form.get('old_question_type_name'), request.form.get('new_question_type_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    
@app.route('/delete_question_type', methods=['GET', 'POST'])
def delete_question_type():
    if request.method == "POST":
        update_db_entry(
            "questions",
            "question_type_id = NULL",
            "question_type_id = \"%s\"" % (request.form.get('question_type_id'))
        )
        delete_db_entry(
            "question_type",
            "question_type_id = \"%s\"" % (request.form.get('question_type_id'))
        )
        flash("Question type %s deleted" % (request.form.get('question_type_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    
# Question Scoring Type

@app.route('/question_scoring_type_maker', methods=['GET', 'POST'])
def question_scoring_type_maker():
    # Check to see if the user is an admin
    if admin_check():
        # Gets all question scoring types
        question_scoring_types = get_entries_from_db(
            "*",
            "question_scoring_type",
            "question_scoring_type_id IS NOT NULL"
        )

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/other/question_scoring_type_maker.html",
            name                    = "Question Scoring Type Maker",
            question_scoring_types  = question_scoring_types
        )
    
    else:
        return redirect(url_for(
            'home'
        )) 

@app.route('/add_question_scoring_type', methods=['GET', 'POST'])
def add_question_scoring_type():
    if request.method == "POST":
        insert_db_entry(
            "question_scoring_type",
            "question_scoring_type_name, question_scoring_type_description",
            "\"%s\", \"%s\"" % (fix_string(request.form.get('question_scoring_type_name')), fix_string(request.form.get('question_scoring_type_description')))
        )
        flash("Question scoring type %s created" % (request.form.get('question_scoring_type_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/update_question_scoring_type', methods=['GET', 'POST'])
def update_question_scoring_type():
    if request.method == "POST":
        update_db_entry(
            "question_scoring_type",
            "question_scoring_type_name = \"%s\", question_scoring_type_description = \"%s\"" % (fix_string(request.form.get('new_question_scoring_type_name')), fix_string(request.form.get('new_question_scoring_type_description'))),
            "question_scoring_type_id = \"%s\"" % (request.form.get('question_scoring_type_id'))
        )
        flash("Question scoring type %s updated to %s" % (request.form.get('old_question_scoring_type_name'), request.form.get('new_question_scoring_type_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    
@app.route('/delete_question_scoring_type', methods=['GET', 'POST'])
def delete_question_scoring_type():
    if request.method == "POST":
        update_db_entry(
            "questions",
            "question_scoring_type_id = NULL",
            "question_scoring_type_id = \"%s\"" % (request.form.get('question_scoring_type_id'))
        )
        delete_db_entry(
            "question_scoring_type",
            "question_scoring_type_id = \"%s\"" % (request.form.get('question_scoring_type_id'))
        )
        flash("Question scoring type %s deleted" % (request.form.get('question_scoring_type_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    

# ADD ROUNDS TO QUIZ
@app.route('/associate_round', methods=['GET', 'POST'])
def associate_round():
    if request.method == "POST":
        # Need to find how many rounds are in the quiz
        number_of_associated_rounds = get_entries_from_db(
            "round_id",
            "live",
            "quiz_id = \"%s\" AND round_id IS NOT NULL" % (request.form.get('quiz_id'))
        )

        unique_associated_rounds = set()
        for associated_round in number_of_associated_rounds:
            unique_associated_rounds.add(associated_round["round_id"])

        number_of_associated_rounds = len(unique_associated_rounds)+1

        insert_db_entry(
            "live",
            "quiz_id, round_id, round_order",
            "%s, %s, %s" % (request.form.get('quiz_id'), request.form.get('round_id'), number_of_associated_rounds)
        )

        flash("Round added to Quiz")
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/unassociate_round', methods=['GET', 'POST'])
def unassociate_round():
    if request.method == "POST":
        delete_db_entry(
            "live",
            "quiz_id = \"%s\" AND round_id = \"%s\"" % (request.form.get('quiz_id'), request.form.get('round_id'))
        )

        # Need to find how many rounds are in the quiz
        number_of_associated_rounds = get_entries_from_db(
            "round_id",
            "live",
            "quiz_id = \"%s\" AND round_id IS NOT NULL" % (request.form.get('quiz_id'))
        )

        unique_associated_rounds = set()
        for associated_round in number_of_associated_rounds:
            unique_associated_rounds.add(associated_round["round_id"])

        number_of_associated_rounds = len(unique_associated_rounds) +1

        # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
        for i in range(int(request.form.get('round_order')), number_of_associated_rounds):
            update_db_entry(
                "live",
                "round_order = %s" % (i),
                "quiz_id = \"%s\" AND round_order = \"%s\"" % (request.form.get('quiz_id'), i+1)
            )

        flash("Round %s removed from Quiz" % (request.form.get('round_name')))
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

# Hints
@app.route('/add_hint', methods=['GET', 'POST'])
def add_hint():
    if request.method == "POST":
        # Find if there are any hints already created for this Question
        number_of_associated_hints = get_entries_from_db(
            "hint_id",
            "hints",
            "question_id = \"%s\"" % (request.form.get('question_id'))
        )

        number_of_associated_hints = len(number_of_associated_hints)+1

        insert_db_entry(
            "hints",
            "question_id, hint_text, hint_number",
            "\"%s\", \"%s\", \"%s\"" % (request.form.get('question_id'), fix_string(request.form.get('hint_text')), number_of_associated_hints)
        )

        flash("Hint added to Question")
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )


    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/update_hint', methods=['GET', 'POST'])
def update_hint():
    if request.method == "POST":
        update_db_entry(
            "hints",
            "hint_text = \"%s\"" % (fix_string(request.form.get('hint_text'))),
            "hint_id = \"%s\"" % (request.form.get('hint_id'))
        )

        flash("Hint updated")
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
          

    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ),
            code = 307    
        )
    
@app.route('/delete_hint', methods=['GET', 'POST'])
def delete_hint():
    if request.method == "POST":
        delete_db_entry(
            "hints",
            "hint_id = \"%s\"" % (request.form.get('hint_id'))
        )

        # Need to find how many rounds are in the quiz
        number_of_associated_hints = get_entries_from_db(
            "hint_id",
            "hints",
            "question_id = \"%s\"" % (request.form.get('question_id'))
        )

        number_of_associated_hints = len(number_of_associated_hints) +1

        # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
        for i in range(int(request.form.get('hint_number')), number_of_associated_hints):
            update_db_entry(
                "hints",
                "hint_number = %s" % (i),
                "question_id = \"%s\" AND hint_number = \"%s\"" % (request.form.get('question_id'), i+1)
            )

        flash("Hint deleted")
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))


# ROUNDS #

@app.route('/round_maker', methods=['GET', 'POST'])
def round_maker():
    # Check to see if the user is an admin
    if admin_check():
        # Gets all quizzes from the quiz table
        round_info = get_entries_from_db(
            "round_id, round_name, round_description",
            "rounds",
            "round_id IS NOT NULL"
        )
        associated_quiz_info=[]
       
        for round in round_info:
            associated_quizzes = []
            # Collects information on all the quizzes this round is associated with
            associated_quiz_info = common_values(
                "quizzes.quiz_name",
                "quizzes",
                "live",
                "quizzes.quiz_id",
                "live.quiz_id WHERE live.round_id = %s" % (round['round_id'])
            )
            for associated_quiz in associated_quiz_info:
                associated_quizzes.append(associated_quiz['quiz_name'])

            round['number_of_associated_quizzes'] = len(associated_quizzes)
            round['associated_quizzes'] = " and ".join(associated_quizzes)

            associated_questions = []
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_tag, questions.question_difficulty, questions.question_points, questions.question_category_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (round['round_id'])
            )
            for associated_question in associated_question_info:
                associated_questions.append(associated_question['question_tag'])

            round['number_of_associated_questions'] = len(associated_questions)
            round['associated_questions'] = " and ".join(associated_questions)

            if associated_question_info:
                # Average question difficulty
                round['average_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                round['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    round['mode_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        round['mode_category'] = "Not set"


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/rounds/round_maker.html",
            name                    = "Round Maker",
            round_info              = round_info,
            associated_quiz_info    = associated_quiz_info
        )
    
    else:
        return redirect(url_for(
            'home'
        )) 

# This will create a new Round
@app.route('/create_new_round', methods=['GET', 'POST'])
def create_new_round():
    # Check to see if the user is an admin
    if admin_check() and request.method == "POST":
            # Inserts the Round into the rounds table, using the no_of_rounds +1 as its unique identifier
            insert_db_entry(
                "rounds",
                "round_name",
                "\"%s\"" % (fix_string(request.form.get('round_name')))
            )         
            
            # Redirects users to the Round template html page, specific to the Round just created
            flash("Round %s, created" % (request.form.get('round_name')))            
            return redirect(url_for(
                "round_maker"
            ))

    else:
        flash("You either aren't authorised to create a round, or you tried to do it via unofficial means")
        return redirect(url_for(
            'home'
        ))


# This function will delete a round from the database, based on the Round id.
@app.route('/delete_round', methods=['GET', 'POST'])
def delete_round():
    # Check to see if the user is an admin
    if admin_check() and request.method == "POST":
        # This finds out all the live table entries involving the round
        associated_quizzes = get_entries_from_db(
            "quiz_id",
            "live",
            "round_id = \"%s\"" % (request.form.get('round_id'))
        )

        round_name = get_entry_from_db(
            "round_name",
            "rounds",
            "round_id = \"%s\"" % (request.form.get('round_id'))
        )

        unique_associated_quizzes_id = set()
        for associated_quiz in associated_quizzes:
            unique_associated_quizzes_id.add(associated_quiz["quiz_id"])

        unique_associated_quizzes = []
        for unique_associated_quiz in unique_associated_quizzes_id:
            all_unique_associated_quizzes = get_entry_from_db(
                "quiz_id, round_order",
                "live",
                "quiz_id = \"%s\" AND round_id = \"%s\"" % (unique_associated_quiz, request.form.get('round_id'))
            )
            unique_associated_quizzes.append(all_unique_associated_quizzes)


        # Deletes the Round from the rounds table in the database based off the round_id
        delete_db_entry(
            "rounds",
            "round_id = \"%s\"" % (request.form.get('round_id'))
        )

        # This if statement doesn't work
        if unique_associated_quizzes is not None:
            for quiz in unique_associated_quizzes:
                # Need to find how many rounds are in the quiz
                number_of_associated_rounds = get_entries_from_db(
                    "round_id",
                    "live",
                    "quiz_id = \"%s\"" % (quiz['quiz_id'])
                )

                unique_associated_rounds = set()
                for associated_round in number_of_associated_rounds:
                    unique_associated_rounds.add(associated_round["round_id"])

                number_of_associated_rounds = len(unique_associated_rounds) +1

                # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
                for i in range(int(quiz['round_order']), number_of_associated_rounds):
                    update_db_entry(
                        "live",
                        "round_order = %s" % (i),
                        "quiz_id = \"%s\" AND round_order = \"%s\"" % (quiz['quiz_id'], i+1)
                    )


        # Redirects users to the quiz template based on the quiz_id
        flash("Round %s, deleted" % (round_name['round_name']))
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )
    
    else:
        flash("Something didn't go as planned")
        return redirect(url_for(
            'home'
        ))  


# QUESTIONS #

@app.route('/question_maker', methods=['GET', 'POST'])
def question_maker():
    # Check to see if the user is an admin
    if admin_check():
        # Gets all quizzes from the quiz table
        question_info = get_entries_from_db(
            "question_id, question_tag, question_category_id, question_difficulty, question_points",
            "questions",
            "question_id IS NOT NULL"
        )

        for question in question_info:
            if question['question_category_id']:
                question_category = get_entry_from_db(
                    "category_name",
                    "categories",
                    "category_id = %s" % (question['question_category_id'])
                )

                question['question_category']=question_category['category_name']

            associated_rounds = []
            # Collects information on all the quizzes this round is associated with
            associated_round_info = common_values(
                "rounds.round_name, rounds.round_id",
                "rounds",
                "live",
                "rounds.round_id",
                "live.round_id WHERE live.question_id = %s" % (question['question_id'])
            )
            for associated_round in associated_round_info:
                associated_rounds.append(associated_round['round_name'])

            question['number_of_associated_rounds'] = len(associated_rounds)
            question['associated_rounds'] = " and ".join(associated_rounds)

            associated_quizzes = []
            for round in associated_round_info:
                # Collects information on all the quizzes this round is associated with
                associated_quiz_info = common_values(
                    "quizzes.quiz_name",
                    "quizzes",
                    "live",
                    "quizzes.quiz_id",
                    "live.quiz_id WHERE live.round_id = %s" % (round['round_id'])
                )
                for associated_quiz in associated_quiz_info:
                    associated_quizzes.append(associated_quiz['quiz_name'])

            associated_quizzes = set(associated_quizzes)
            question['associated_quizzes'] = " and ".join(associated_quizzes)
            question['number_of_associated_quizzes'] = len(associated_quizzes)


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/questions/question_maker.html",
            name                    = "Question Maker",
            question_info           = question_info
        )
    
    else:
        return redirect(url_for(
            'home'
        )) 


# Creates a question not associated to any quiz or round
@app.route('/create_new_question', methods=['GET', 'POST'])
def create_new_question():
    if admin_check() and request.method == "POST":
        if check_single_db(
            "question_type_id",
            "question_type",
            "question_type_id IS NOT NULL"
        ):
            question_type_id = get_entry_from_db(
                "question_type_id",
                "question_type",
                "question_type_id IS NOT NULL"
            )['question_type_id']

        else:
            # Redirects user to the Question template for the newly created Question
            flash("You need to create a Question Type first")
            return redirect(url_for(
                request.form.get("source_point")
            ))  
        
        if check_single_db(
            "category_id",
            "categories",
            "category_id IS NOT NULL"
        ):
            question_category_id = get_entry_from_db(
                "category_id",
                "categories",
                "category_id IS NOT NULL"
            )['category_id']
        else:
            # Redirects user to the Question template for the newly created Question
            flash("You need to create a Category first")
            return redirect(url_for(
                request.form.get("source_point")
            ))  

        if check_single_db(
            "question_scoring_type_id",
            "question_scoring_type",
            "question_scoring_type_id IS NOT NULL"
        ):
            question_scoring_type_id = get_entry_from_db(
                "question_scoring_type_id",
                "question_scoring_type",
                "question_scoring_type_id IS NOT NULL"
            )['question_scoring_type_id']
        else:
            # Redirects user to the Question template for the newly created Question
            flash("You need to create a Question Scoring Type first")
            return redirect(url_for(
                request.form.get("source_point")
            ))  

        if question_type_id and question_category_id and question_scoring_type_id:
            # Creates a new Question in the database, with default values
            insert_db_entry(
                "questions",
                "question_tag, question_type_id, question_category_id, question_points, question_scoring_type_id, question_difficulty",
                "\"%s\", \"%s\", \"%s\", \"10\", \"%s\", \"5\"" % (fix_string(request.form.get('question_tag')), question_type_id, question_category_id, question_scoring_type_id)
            )

            # Redirects user to the Question template for the newly created Question
            flash("Question created")
            return redirect(url_for(
                request.form.get("source_point")
            ))       
    
    else:
        return redirect(url_for(
            'home'
        ))


@app.route('/delete_question', methods=['GET', 'POST'])
def delete_question():
    if admin_check() and request.method == "POST":
        # This finds out all the live table entries involving the round
        associated_rounds = get_entries_from_db(
            "round_id",
            "live",
            "question_id = \"%s\"" % (request.form.get('question_id'))
        )

        unique_associated_rounds_id = set()
        for associated_round in associated_rounds:
            unique_associated_rounds_id.add(associated_round["round_id"])

        unique_associated_rounds = []
        for unique_associated_round in unique_associated_rounds_id:
            all_unique_associated_rounds = get_entry_from_db(
                "round_id, question_order",
                "live",
                "round_id = \"%s\" AND question_id = \"%s\"" % (unique_associated_round, request.form.get('question_id'))
            )
            unique_associated_rounds.append(all_unique_associated_rounds)

        # Removes the Question from the questions table in the database
        delete_db_entry(
            "questions",
            "question_id = %s" % (request.form.get('question_id'))
        )

        if unique_associated_rounds is not None:
            for round in unique_associated_rounds:
                # Need to find how many rounds are in the quiz
                number_of_associated_questions = get_entries_from_db(
                    "question_id",
                    "live",
                    "round_id = \"%s\"" %  (round['round_id'])
                )

                unique_associated_questions = set()
                for associated_question in number_of_associated_questions:
                    unique_associated_questions.add(associated_question["question_id"])

                number_of_associated_questions = len(unique_associated_questions) +1

                # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
                for i in range(int(round['question_order']), number_of_associated_questions):
                    update_db_entry(
                        "live",
                        "question_order = %s" % (i),
                        "round_id = \"%s\" AND question_order = \"%s\"" % (round['round_id'], i+1)
                    )


        flash("Question deleted")
        return redirect(url_for(
            request.form.get("source_point")
        ))


    else:
        return redirect(url_for(
            'home'
        ))
    

@app.route('/associate_question', methods=['GET', 'POST'])
def associate_question():
    if request.method == "POST":
        # Need to find how many questions are in the round
        associated_questions = get_entries_from_db(
            "question_id",
            "live",
            "round_id = \"%s\" AND question_id IS NOT NULL" % (request.form.get('round_id'))
        )

        unique_associated_questions = set()
        for associated_question in associated_questions:
            unique_associated_questions.add(associated_question["question_id"])

        number_of_associated_questions = len(unique_associated_questions)+1

        insert_db_entry(
            "live",
            "round_id, question_id, question_order",
            "%s, %s, %s" % (request.form.get('round_id'), request.form.get('question_id'), number_of_associated_questions)
        )

        flash("Question added to Round")
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/unassociate_question', methods=['GET', 'POST'])
def unassociate_question():
    if request.method == "POST":
        delete_db_entry(
            "live",
            "question_id = \"%s\" AND round_id = \"%s\"" % (request.form.get('question_id'), request.form.get('round_id'))
        )

        # Need to find how many questions are in the round
        number_of_associated_questions = get_entries_from_db(
            "question_id",
            "live",
            "round_id = \"%s\" AND question_id IS NOT NULL" % (request.form.get('round_id'))
        )

        unique_associated_questions = set()
        for associated_question in number_of_associated_questions:
            unique_associated_questions.add(associated_question["question_id"])

        number_of_associated_questions = len(unique_associated_questions) +1

        # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
        for i in range(int(request.form.get('question_order')), number_of_associated_questions):
            update_db_entry(
                "live",
                "question_order = %s" % (i),
                "round_id = \"%s\" AND question_order = \"%s\"" % (request.form.get('round_id'), i+1)
            )

        flash("Question removed from Round")
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
  

# Question Media #
# These need creating
@app.route('/add_question_media', methods=['GET', 'POST'])
def add_question_media():
    if request.method == "POST":
        insert_db_entry(
            "question_media",
            "question_id, question_media_url, question_media_type, question_media_description",
            "\"%s\", \"%s\", \"%s\", \"%s\"" % (request.form.get('question_id'), request.form.get('question_media_url'), request.form.get('question_media_type'), request.form.get('question_media_description'))
        )

        flash("Added %s to Question" % (request.form.get('question_media_type')))
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))

@app.route('/update_question_media', methods=['GET', 'POST'])
def update_question_media():
    if request.method == "POST":
        update_db_entry(
            "question_media",
            "question_media_url = \"%s\", question_media_type = \"%s\", question_media_description = \"%s\"" % (fix_string(request.form.get('question_media_url')), request.form.get('question_media_type'), fix_string(request.form.get('question_media_description'))),
            "question_media_id = \"%s\"" % (request.form.get('question_media_id'))
        )

        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ),
            code = 307    
        )
    
@app.route('/delete_question_media', methods=['GET', 'POST'])
def delete_question_media():
    if request.method == "POST":
        delete_db_entry(
            "question_media",
            "question_media_id = \"%s\"" % (request.form.get('question_media_id'))
        )

        flash("Media deleted from Question")
        return redirect(url_for(
                request.form.get('source_point')
            ),
                code = 307
            )
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))


# PARTICIPANTS #
 
# This will insert selected users into the participants table for a given quiz
@app.route('/add_participants', methods=['GET', 'POST'])
def add_participants():
    if admin_check() and request.method == "POST":
        # Cycle through the list of users submitted from the form
        for i in request.form.getlist('user_id'):
            # Insert the user into the participants table
            insert_db_entry(
                "participants",
                "user_id, quiz_id, participant_ready, participant_score",
                "\"%s\", \"%s\", \"0\", \"0\"" % (i, request.form.get('quiz_id'))
            )
            update_leaderboard(i, request.form.get('quiz_id'), 0)

        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )


    # Redirect user to the quiz template page for the current quiz
    return redirect(url_for(
        'home'
    ))

# This will remove selected users from the participants table in the database, for a given quiz
@app.route('/remove_participants', methods=['GET', 'POST'])
def remove_participants():

    if admin_check() and request.method == "POST":
        # Cycle through the list of users submitted from the form
        for i in request.form.getlist('username'):
            
            # Retrieve the user_id from the username provided by the form
            user_info= get_entry_from_db(
                "user_id",
                "users",
                "username = \"%s\"" % (i)
            )

            # Delete the user into the participants table
            delete_db_entry(
                "participants",
                "user_id = %s AND quiz_id = %s" % (user_info['user_id'], request.form.get('quiz_id'))
            )

            # Delete the user into the answers table
            delete_db_entry(
                "answers",
                "user_id = %s AND quiz_id = %s" % (user_info['user_id'], request.form.get('quiz_id'))
            )

            # Delete the user into the user_media table
            delete_db_entry(
                "user_media",
                "user_id = %s AND quiz_id = %s" % (user_info['user_id'], request.form.get('quiz_id'))
            )

        # Redirect user to the quiz template page for the current quiz
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )
    
    else:
        return redirect(url_for(
            'home'
        ))

# EDIT     ############################################################################

# QUIZ #

# This will display an overview page for the quiz. Displaying basic information on all its participants, rounds and questions.
@app.route('/quiz_template', methods=['GET', 'POST'])
def quiz_template():
    if admin_check() and request.method == "POST":
        # Checks to see if the quiz exists
        if not check_single_db(
            "quiz_id",
            "quizzes",
            "quiz_id = \"%s\"" % (request.form.get('quiz_id'))
        ):
            # Redirects users to the quiz maker/editor overview page if the quiz doesn't exist
            flash("This quiz does not exist")
            return redirect(url_for(
                'quiz_maker'
            ))

        # Retrieves information about the quiz based of the quiz_id
        quiz_info = get_entry_from_db(
            "quiz_id, quiz_name, quiz_description",
            "quizzes",
            "quiz_id = \"%s\"" % (request.form.get('quiz_id'))
        )

        # Collects information on all the rounds associated with the quiz
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.round_order",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.quiz_id = %s" % (request.form.get('quiz_id'))
        )

        # Sorts the dictionaries of rounds in order of their round_order
        associated_round_info = sorted(associated_round_info, key=lambda k: k['round_order'])


        quiz_info['number_of_associated_rounds'] = len(associated_round_info)

        associated_questions = []
        for round in associated_round_info:
            associated_questions_names = []
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (round['round_id'])
            )
            for associated_question in associated_question_info:
                associated_questions.append(associated_question)
                associated_questions_names.append(associated_question['question_tag'])
            
            round['number_of_associated_questions'] = len(associated_question_info)
            round['associated_questions'] = " and ".join(associated_questions_names)
            
            if associated_question_info:
                # Average question difficulty
                round['average_question_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                round['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    round['mode_question_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        round['mode_question_category'] = "Not set"

        # associated_questions = set(associated_questions)
        quiz_info['number_of_associated_questions'] = len(associated_questions)

        if associated_questions:
            # Average question difficulty
            quiz_info['average_question_difficulty'] = average(associated_questions, "question_difficulty")
            # Total question points
            quiz_info['total_points'] = total(associated_questions, "question_points")
            # Mode question category
            question_category_id = mode(associated_questions, "question_category_id")
            if question_category_id == []:
                quiz_info['mode_question_category'] = "None set"
            else:
                if len(question_category_id) > 1:
                    mode_question_categories = []
                    for question_category in question_category_id:
                        question_category_name = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category)
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    quiz_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    quiz_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (question_category_id[0])
                    )['category_name']
                else:
                    quiz_info['mode_question_category'] = "Not set"


        # This finds all the rounds not currentlu associated with the current quiz
        unassociated_round_info = compare_two_tables(
            "round_id, round_name, round_description",
            "rounds",
            "round_id",
            "live",
            "quiz_id = \"%s\"" % (request.form.get('quiz_id'))
        )


        associated_questions = []
        for round in unassociated_round_info:
            associated_questions_names = []
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (round['round_id'])
            )
            for associated_question in associated_question_info:
                associated_questions.append(associated_question)
                associated_questions_names.append(associated_question['question_tag'])
            
            round['number_of_associated_questions'] = len(associated_question_info)
            round['associated_questions'] = " and ".join(associated_questions_names)
            
            if associated_question_info:
                # Average question difficulty
                round['average_question_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                round['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    round['mode_question_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        round['mode_question_category'] = "Not set"


        # Returns all users who aren't already in the participant table
        user_info = compare_two_tables(
            "username, user_id",
            "users",
            "user_id",
            "participants",
            "quiz_id = \"%s\"" % (request.form.get('quiz_id'))
        )

        # Returns all users from the participant table, whilst grabbing their associated username from the users table
        participant_info = common_values_not_unique(
            "username",
            "users",
            "user_id",
            "participants",
            "quiz_id = \"%s\"" % (request.form.get('quiz_id'))
        )

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/quizzes/quiz_template.html",
            name                    = "Quiz Template",
            quiz_info               = quiz_info, 
            unassociated_round_info = unassociated_round_info,
            associated_round_info   = associated_round_info,
            user_info               = user_info,
            participant_info        = participant_info
        )

    else:
        flash("Cheeky")
        return redirect(url_for(
            'home'
        ))
    

# This will change the quiz name to something else unique
@app.route('/update_quiz_name', methods=['GET', 'POST'])
def update_quiz_name():
    if admin_check() and request.method == "POST":
        # Checks if the new quiz name is unique
        if check_single_db(
            "quiz_id",
            "quizzes",
            "quiz_name = \"%s\"" % (fix_string(request.form.get('new_quiz_name')))
        ):
            # If the quiz name is already in use, then the quiz name is not updated
            flash('That quiz name is already in use.')

        else:
            # If unqiue, then the quiz Name is updated
            update_db_entry(
                "quizzes",
                "quiz_name = \"%s\"" % (fix_string(request.form.get('new_quiz_name'))),
                "quiz_id = %s" % (request.form.get('quiz_id'))
            )
            flash('Quiz name updated to %s' % (request.form.get('new_quiz_name')))

        # Redirects user to quiz template 
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )


# This will change the quiz name to something else unique
@app.route('/update_quiz_description', methods=['GET', 'POST'])
def update_quiz_description():
    if admin_check() and request.method == "POST":
        # If unqiue, then the quiz Name is updated
        update_db_entry(
            "quizzes",
            "quiz_description = \"%s\"" % (fix_string(request.form.get('new_quiz_description'))),
            "quiz_id = %s" % (request.form.get('quiz_id'))
        )

        # Redirects user to quiz template 
        flash('Quiz description updated')
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )


# ROUNDS #

# This will display an overview page for the Round. Displaying it's associated quiz and basic information on its questions.
@app.route('/round_template', methods=['GET', 'POST'])
def round_template():

    if admin_check() and request.method == "POST":
        # Checks to see if a Round with the request round_id exists in the rounds table in the database
        if not check_single_db(
            "round_id",
            "rounds",
            "round_id = %s" % (request.form.get('round_id'))
        ):
            # If the Round does not exists, then the user is redirected to the quiz Maker/Editor overview page
            flash("This Round does not exist")
            return redirect(url_for(
                'round_maker'
            ))


        # Retrieves information about the quiz based of the quiz_id
        round_info = get_entry_from_db(
            "round_id, round_name, round_description",
            "rounds",
            "round_id = \"%s\"" % (request.form.get('round_id'))
        )

        # Collects information on all the quizzes this round is associated with
        associated_quiz_info = common_values(
            "quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description, live.round_order",
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE live.round_id = %s" % (request.form.get('round_id'))
        )

        # Sorts the dictionaries of rounds in order of their round_order
        associated_quiz_info = sorted(associated_quiz_info, key=lambda k: (k['quiz_name'] is not None, k['quiz_name']))

        for quiz in associated_quiz_info:
            associated_rounds = []
            # Collects information on all the quizzes this round is associated with
            associated_round_info = common_values(
                "rounds.round_name, rounds.round_id",
                "rounds",
                "live",
                "rounds.round_id",
                "live.round_id WHERE live.quiz_id = %s" % (quiz['quiz_id'])
            )
            for associated_round in associated_round_info:
                associated_rounds.append(associated_round['round_name'])

            quiz['number_of_associated_rounds'] = len(associated_rounds)
            quiz['associated_rounds'] = " and ".join(associated_rounds)

            associated_questions = []
            for round in associated_round_info:
                # Collects information on all the quizzes this round is associated with
                associated_question_info = common_values(
                    "questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points",
                    "questions",
                    "live",
                    "questions.question_id",
                    "live.question_id WHERE live.round_id = %s" % (round['round_id'])
                )
                for associated_question in associated_question_info:
                    associated_questions.append(associated_question['question_tag'])

            # associated_questions = set(associated_questions)
            quiz['associated_questions'] = " and ".join(associated_questions)
            quiz['number_of_associated_questions'] = len(associated_questions)

            if associated_questions:
                # Average question difficulty
                quiz['average_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                quiz['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    quiz['mode_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        quiz['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        quiz['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        quiz['mode_category'] = "Not set"




        # Number of associated quizzes
        round_info['number_of_associated_quizzes'] = len(associated_quiz_info)

        # This finds all the quizzes this round is not currently associated with
        unassociated_quiz_info = compare_two_tables_new_quizzes(
            request.form.get('round_id')
        )

        # This removes all the duplicate questions
        unassociated_quiz_info = remove_dictionary_duplicates(unassociated_quiz_info, "quiz_id")
        # This removes the question if it appears in the associated list
        unassociated_quiz_info = compare_dictionary_lists(unassociated_quiz_info, associated_quiz_info, "quiz_id")

        for quiz in unassociated_quiz_info:
            associated_rounds = []
            # Collects information on all the quizzes this round is associated with
            associated_round_info = common_values(
                "rounds.round_name, rounds.round_id",
                "rounds",
                "live",
                "rounds.round_id",
                "live.round_id WHERE live.quiz_id = %s" % (quiz['quiz_id'])
            )
            for associated_round in associated_round_info:
                associated_rounds.append(associated_round['round_name'])

            quiz['number_of_associated_rounds'] = len(associated_rounds)
            quiz['associated_rounds'] = " and ".join(associated_rounds)

            associated_questions = []
            for round in associated_round_info:
                # Collects information on all the quizzes this round is associated with
                associated_question_info = common_values(
                    "questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points",
                    "questions",
                    "live",
                    "questions.question_id",
                    "live.question_id WHERE live.round_id = %s" % (round['round_id'])
                )
                for associated_question in associated_question_info:
                    associated_questions.append(associated_question['question_tag'])

            # associated_questions = set(associated_questions)
            quiz['associated_questions'] = " and ".join(associated_questions)
            quiz['number_of_associated_questions'] = len(associated_questions)

            if associated_questions:
                # Average question difficulty
                quiz['average_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                quiz['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    quiz['mode_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        quiz['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        quiz['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        quiz['mode_category'] = "Not set"
        

        # Collects information on all the quizzes this round is associated with
        associated_question_info = common_values(
            "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_points, questions.question_difficulty, live.question_order, live.round_id",
            "questions",
            "live",
            "questions.question_id",
            "live.question_id WHERE live.round_id = %s" % (request.form.get('round_id'))
        )

        if associated_question_info:
            for associated_question in associated_question_info:
                associated_round_names =[]
                associated_question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (associated_question['question_category_id'])
                    )['category_name']
                
                associated_round_info = common_values(
                    "rounds.round_name",
                    "rounds",
                    "live",
                    "rounds.round_id",
                    "live.round_id WHERE live.question_id = %s" % (associated_question['question_id'])
                )
                
                for associated_round in associated_round_info:
                    associated_round_names.append(associated_round['round_name'])
                
                associated_question['number_of_associated_rounds'] = len(associated_round_names)
                associated_question['associated_rounds'] = " and ".join(associated_round_names)


            # Number of associated questions
            round_info['number_of_associated_questions'] = len(associated_question_info)
            # Average question difficulty
            round_info['average_question_difficulty'] = average(associated_question_info, "question_difficulty")
            # Total question points
            round_info['total_points'] = total(associated_question_info, "question_points")
            # Mode question category
            question_category_id = mode(associated_question_info, "question_category_id")
            if question_category_id == []:
                round_info['mode_question_category'] = "None set"
            else:
                if len(question_category_id) > 1:
                    mode_question_categories = []
                    for question_category in question_category_id:
                        question_category_name = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category)
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    round_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    round_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (question_category_id[0])
                    )['category_name']
                else:
                    round_info['mode_question_category'] = "Not set"


        # Sorts the dictionaries of rounds in order of their round_order
        associated_question_info = sorted(associated_question_info, key=lambda k: k['question_order']) 

        #This finds all the quizzes this round is not currentlu associated with
        unassociated_question_info = compare_two_tables_new_questions(
            request.form.get('round_id')
        )

        unassociated_question_info = sorted(unassociated_question_info, key=lambda k: (k['round_id'] is not None, k['round_id']))
        # # This removes all the duplicate questions
        unassociated_question_info = remove_dictionary_duplicates(unassociated_question_info, "question_id")
        # # This removes the question if it appears in the associated list
        unassociated_question_info = compare_dictionary_lists(unassociated_question_info, associated_question_info, "question_id")

        if unassociated_question_info:
            for unassociated_question in unassociated_question_info:
                associated_round_names =[]
                unassociated_question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (unassociated_question['question_category_id'])
                    )['category_name']
                
                associated_round_info = common_values(
                    "rounds.round_name",
                    "rounds",
                    "live",
                    "rounds.round_id",
                    "live.round_id WHERE live.question_id = %s" % (unassociated_question['question_id'])
                )
                
                for associated_round in associated_round_info:
                    associated_round_names.append(associated_round['round_name'])
                
                unassociated_question['number_of_associated_rounds'] = len(associated_round_names)
                unassociated_question['associated_rounds'] = " and ".join(associated_round_names)


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/rounds/round_template.html",
            name                        = "Round Template",
            round_info                  = round_info,
            associated_quiz_info        = associated_quiz_info,
            unassociated_quiz_info      = unassociated_quiz_info,
            associated_question_info    = associated_question_info,
            unassociated_question_info  = unassociated_question_info
        )


# This function will update the current Round's name, but only if the new name doesn't already exist for a Round in the associated quiz
@app.route('/update_round_name', methods=['GET', 'POST']) 
def update_round_name():
    # Check to see if the user is an admin       
    if admin_check and request.method == "POST":
        # If there's not already a Round with that name in the quiz, the round_name is updated
        update_db_entry(
            "rounds",
            "round_name = \"%s\"" % (fix_string(request.form.get('new_round_name'))),
            "round_id = %s" % (request.form.get('round_id'))
        )

        # Redirects user to Round template 
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )
    
    else:
        return redirect(url_for(
            'home'
        )) 

# This function will update the current Round's name, but only if the new name doesn't already exist for a Round in the associated quiz
@app.route('/update_round_description', methods=['GET', 'POST']) 
def update_round_description():
    # Check to see if the user is an admin
    if admin_check and request.method == "POST":
        # If there's not already a Round with that name in the quiz, the round_name is updated
        update_db_entry(
            "rounds",
            "round_description = \"%s\"" % (fix_string(request.form.get('new_round_description'))),
            "round_id = %s" % (request.form.get('round_id'))
        )

        flash("Round description updated")
        # The user is redirected to where they clicked the button
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )

    
    else:
        return redirect(url_for('home'))  


# QUESTIONS #

# This will display a detailed overview page for the Question, with the ability to edit each aspect.
@app.route('/question_template', methods=['GET', 'POST'])
def question_template():

    if admin_check() and request.method == "POST":
        # Checks to see if a Round with the request round_id exists in the rounds table in the database
        if not check_single_db(
            "question_id",
            "questions",
            "question_id = %s" % (request.form.get('question_id'))
        ):
            # If the Round does not exists, then the user is redirected to the quiz Maker/Editor overview page
            flash("This Question does not exist")
            return redirect(url_for(
                'question_maker'
            ))


        # Retrieves information about the quiz based of the quiz_id
        question_info = get_entry_from_db(
            "question_id, question_text, question_tag, question_correct_answer, question_points, question_difficulty, question_type_id, question_scoring_type_id, question_category_id",
            "questions",
            "question_id = \"%s\"" % (request.form.get('question_id'))
        )

        # Question Type information
        if question_info['question_correct_answer'] is not None:
            clean_text, urls = detect_urls(question_info['question_correct_answer'])
            if urls:
                question_info['question_correct_answer'] = clean_text
                question_info['urls'] = urls


        # Question Type information
        if question_info['question_type_id'] is not None:
            question_type = get_entry_from_db(
                "*",
                "question_type",
                "question_type_id = \"%s\"" % (question_info['question_type_id'])
            )

            question_info.update(question_type)


            # This finds all the quizzes this round is not currentlu associated with
            question_types = compare_two_tables(
                "*",
                "question_type",
                "question_type_id",
                "questions",
                "question_id = \"%s\"" % (request.form.get('question_id'))
            )

        else:
            question_types = get_entries_from_db(
               "*",
                "question_type",
                "question_type_id is NOT NULL"
            )

        # Question Scoring Type information
        if question_info['question_scoring_type_id'] is not None:
            question_scoring_type = get_entry_from_db(
                "*",
                "question_scoring_type",
                "question_scoring_type_id = \"%s\"" % (question_info['question_scoring_type_id'])
            )

            question_info.update(question_scoring_type)


            # This finds all the quizzes this round is not currentlu associated with
            question_scoring_types = compare_two_tables(
                "*",
                "question_scoring_type",
                "question_scoring_type_id",
                "questions",
                "question_id = \"%s\"" % (request.form.get('question_id'))
            )

        else:
            question_scoring_types = get_entries_from_db(
               "*",
                "question_scoring_type",
                "question_scoring_type_id is NOT NULL"
            )

        # Question Category information
        if question_info['question_category_id'] is not None:
            question_category = get_entry_from_db(
                "*",
                "categories",
                "category_id = \"%s\"" % (question_info['question_category_id'])
            )

            question_info.update(question_category)


            # This finds all the quizzes this round is not currentlu associated with
            question_categories = compare_two_tables_name(
                "*",
                "categories",
                "category_id",
                "question_category_id",
                "questions",
                "question_id = \"%s\"" % (request.form.get('question_id'))
            )

        else:
            question_categories = get_entries_from_db(
               "*",
                "categories",
                "category_id is NOT NULL"
            )

        # Question Hints information
        hints = get_entries_from_db(
            "*",
            "hints",
            "question_id = \"%s\"" % (request.form.get('question_id'))
        )

        hints = sorted(hints, key=lambda k: k['hint_number']) 

        question_media_info = get_entries_from_db(
            "*",
            "question_media",
            "question_id = \"%s\"" % (request.form.get('question_id'))
        )


        # Round information
        # Collects information on all the rounds this question is associated with
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.question_order",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.question_id = %s" % (request.form.get('question_id'))
        )

        # Loop through all the associated rounds to find their associated quizzes
        for associated_round in associated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_points, questions.question_difficulty, live.question_order, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (associated_round['round_id'])
            )

            if associated_question_info:
                # Number of associated questions
                associated_round['number_of_associated_questions'] = len(associated_question_info)

                # Names of the associated questions
                question_names =[]
                for question in associated_question_info:
                    question_names.append(question['question_tag'])
                associated_round['question_names'] = ' and '.join([str(elem) for elem in question_names])

                # Average question difficulty
                associated_round['average_question_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                associated_round['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    associated_round['mode_question_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        associated_round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        associated_round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        associated_round['mode_question_category'] = "Not set"



            quiz_names = []
            # Question Category information
            quiz_info = common_values(
                "quizzes.quiz_name",
                "quizzes",
                "live",
                "quizzes.quiz_id",
                "live.quiz_id WHERE live.round_id = \"%s\"" % (associated_round['round_id'])
            )

            for quiz in quiz_info:
                quiz_names.append(quiz['quiz_name'])
            associated_round['quiz_names'] = ' and '.join([str(elem) for elem in quiz_names])
            associated_round['number_of_associated_quizzes'] = len(quiz_names)

        # Sorts the dictionaries of rounds in order of their round_order
        associated_round_info = sorted(associated_round_info, key=lambda k: k['round_name']) 
        question_info['number_of_associated_rounds'] = len(associated_round_info)

        # This finds all the quizzes this round is not currentlu associated with
        unassociated_round_info = compare_two_tables(
            "round_id, round_name, round_description",
            "rounds",
            "round_id",
            "live",
            "question_id = \"%s\"" % (request.form.get('question_id'))
        )

        # Loop through all the associated rounds to find their associated quizzes
        for unassociated_round in unassociated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_points, questions.question_difficulty, live.question_order, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (unassociated_round['round_id'])
            )

            if associated_question_info:
                # Number of associated questions
                unassociated_round['number_of_associated_questions'] = len(associated_question_info)

                # Names of the associated questions
                question_names =[]
                for question in associated_question_info:
                    question_names.append(question['question_tag'])
                unassociated_round['question_names'] = ', '.join([str(elem) for elem in question_names])

                # Average question difficulty
                unassociated_round['average_question_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                unassociated_round['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    unassociated_round['mode_question_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        unassociated_round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        unassociated_round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        unassociated_round['mode_question_category'] = "Not set"

            quiz_names = []
            # Question Category information
            quiz_info = common_values(
                "quizzes.quiz_name",
                "quizzes",
                "live",
                "quizzes.quiz_id",
                "live.quiz_id WHERE live.round_id = \"%s\"" % (unassociated_round['round_id'])
            )

            for quiz in quiz_info:
                quiz_names.append(quiz['quiz_name'])
            unassociated_round['quiz_names'] = ', '.join([str(elem) for elem in quiz_names])
            unassociated_round['number_of_associated_quizzes'] = len(quiz_names)


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/make_a_quiz/questions/question_template.html",
            name                    = "Question Editor",
            question_info           = question_info,
            question_types          = question_types,
            question_scoring_types  = question_scoring_types,
            question_categories     = question_categories,
            hints                   = hints,
            unassociated_round_info = unassociated_round_info,
            associated_round_info   = associated_round_info,
            question_media_info     = question_media_info
        )

    else:
        return redirect(url_for(
            'home'
        ))  


# This will find out what field is being updated and upload that information to the database
@app.route('/update_question', methods=['GET', 'POST'])
def update_question():
    if admin_check() and request.method == "POST":
        # Gets information from the HTML form  
        question_update         = fix_string(request.form.get('question_update'))
        question_update_field   = request.form.get('question_update_field')

        # Format the submitted data to work depending on what was updated
        if re.search("question_audio", question_update_field):
            question_update = re.sub("view", "preview", question_update)
        if re.search("question_video", question_update_field):
            question_update = re.sub("watch\?v\=", "embed/", question_update)

        # Puts quotation marks either side of the question update
        if question_update != "NULL":
            question_update = "\"%s\"" % (question_update)

        # Updates the question in the database    
        update_db_entry(
            "questions",
            "%s = %s" % (question_update_field, question_update),
            "question_id = %s" % (request.form.get('question_id'))
        )

        if any(c in "\r\n" for c in question_update):
            question_update = "new lines"

        # Redirects to the question template
        flash("question updated %s" % (question_update))
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )
    
    else:
        return redirect(url_for(
            'home'
        ))  


# This will update the question or round number orders
@app.route('/change_order', methods=['GET', 'POST'])
def change_order():
    # Check to see if the user is an admin       
    if admin_check() and request.method == "POST":

        # If the new order is lower than the old order
        if int(request.form.get("old_order")) > int(request.form.get("new_order")):
            # Create a list of numbers from the new order to the old order.
            # Python range needs to be range(x,y,s) where x<y and s is step. So making s=-1 you can have a reverse list.
            order = list(range(int(request.form.get("old_order"))-1, int(request.form.get("new_order"))-1, -1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "live",
                "%s_order = 0" % (request.form.get("order_type")),
                "quiz_id = \"%s\" AND round_id = \"%s\" AND %s_order = \"%s\"" % (request.form.get("quiz_id"), request.form.get("round_id"), request.form.get("order_type"), request.form.get("old_order"))
            )

            # This will shift all other orders up 1 from the "new order" to the "old order-1"
            for i in order:
                update_db_entry(
                    "live",
                    "%s_order = %s" % (request.form.get("order_type"), i+1),
                    "quiz_id = \"%s\" AND %s_order = \"%s\"" % (request.form.get("quiz_id"), request.form.get("order_type"), i)
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                "%s_order = %s" % (request.form.get("order_type"), request.form.get("new_order")),
                "quiz_id = \"%s\" AND round_id = \"%s\" AND %s_order = \"0\"" % (request.form.get("quiz_id"), request.form.get("round_id"), request.form.get("order_type"))
            )
    

        # If the new order is higher than the old order 
        else:
            # Create a list of numbers from the old order to the new order.
            order = list(range(int(request.form.get("old_order")),int(request.form.get("new_order"))+1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "live",
                "%s_order = 0" % (request.form.get("order_type")),
                "quiz_id = \"%s\" AND round_id = \"%s\" AND %s_order = \"%s\"" % (request.form.get("quiz_id"), request.form.get("round_id"), request.form.get("order_type"), request.form.get("old_order"))
            )

            # This will shift all other orders down 1 from the "new order +1" to the "old order"
            for i in range(len(order)):
                update_db_entry(
                    "live",
                    "%s_order = %s" % (request.form.get("order_type"), order[i-1]),
                    "quiz_id = \"%s\" AND %s_order = \"%s\"" % (request.form.get("quiz_id"), request.form.get("order_type"), order[i])
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                "%s_order = %s" % (request.form.get("order_type"), request.form.get("new_order")),
                "quiz_id = \"%s\" AND round_id = \"%s\" AND %s_order = 0" % (request.form.get("quiz_id"), request.form.get("round_id"), request.form.get("order_type"))
            )

        # These three if/else statments will return the user back to the appropriate pages
        # If this function was called from the round edit page, then it'll return you to the round edit page
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )
    
    else:
        return redirect(url_for(
            'home'
        ))
    
# This will update the question or round number orders
@app.route('/change_question_order', methods=['GET', 'POST'])
def change_question_order():
    # Check to see if the user is an admin       
    if admin_check() and request.method == "POST":

        # If the new order is lower than the old order
        if int(request.form.get("old_order")) > int(request.form.get("new_order")):
            # Create a list of numbers from the new order to the old order.
            # Python range needs to be range(x,y,s) where x<y and s is step. So making s=-1 you can have a reverse list.
            order = list(range(int(request.form.get("old_order"))-1, int(request.form.get("new_order"))-1, -1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "live",
                "%s_order = 0" % (request.form.get("order_type")),
                "question_id = \"%s\" AND round_id = \"%s\" AND %s_order = \"%s\"" % (request.form.get("question_id"), request.form.get("round_id"), request.form.get("order_type"), request.form.get("old_order"))
            )

            # This will shift all other orders up 1 from the "new order" to the "old order-1"
            for i in order:
                update_db_entry(
                    "live",
                    "%s_order = %s" % (request.form.get("order_type"), i+1),
                    "round_id = \"%s\" AND %s_order = \"%s\"" % (request.form.get("round_id"), request.form.get("order_type"), i)
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                "%s_order = %s" % (request.form.get("order_type"), request.form.get("new_order")),
                "question_id = \"%s\" AND round_id = \"%s\" AND %s_order = \"0\"" % (request.form.get("question_id"), request.form.get("round_id"), request.form.get("order_type"))
            )
    

        # If the new order is higher than the old order 
        else:
            # Create a list of numbers from the old order to the new order.
            order = list(range(int(request.form.get("old_order")),int(request.form.get("new_order"))+1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "live",
                "%s_order = 0" % (request.form.get("order_type")),
                "question_id = \"%s\" AND round_id = \"%s\" AND %s_order = \"%s\"" % (request.form.get("question_id"), request.form.get("round_id"), request.form.get("order_type"), request.form.get("old_order"))
            )

            # This will shift all other orders down 1 from the "new order +1" to the "old order"
            for i in range(len(order)):
                update_db_entry(
                    "live",
                    "%s_order = %s" % (request.form.get("order_type"), order[i-1]),
                    "round_id = \"%s\" AND %s_order = %s" % (request.form.get("round_id"), request.form.get("order_type"), order[i])
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                "%s_order = %s" % (request.form.get("order_type"), request.form.get("new_order")),
                "question_id = \"%s\" AND round_id = \"%s\" AND %s_order = \"0\"" % (request.form.get("question_id"), request.form.get("round_id"), request.form.get("order_type"))
            )

        # These three if/else statments will return the user back to the appropriate pages
        # If this function was called from the round edit page, then it'll return you to the round edit page
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )
    
    else:
        return redirect(url_for(
            'home'
        ))

# This will update the hint orders
@app.route('/change_hint_order', methods=['GET', 'POST'])
def change_hint_order():
    # Check to see if the user is an admin       
    if admin_check() and request.method == "POST":

        # If the new order is lower than the old order
        if int(request.form.get("old_order")) > int(request.form.get("new_order")):
            # Create a list of numbers from the new order to the old order.
            # Python range needs to be range(x,y,s) where x<y and s is step. So making s=-1 you can have a reverse list.
            order = list(range(int(request.form.get("old_order"))-1, int(request.form.get("new_order"))-1, -1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "hints",
                "hint_number = 0",
                "hint_id = \"%s\"" % (request.form.get("hint_id"))
            )

            # This will shift all other orders up 1 from the "new order" to the "old order-1"
            for i in order:
                update_db_entry(
                    "hints",
                    "hint_number = %s" % (i+1),
                    "question_id = \"%s\" AND hint_number = \"%s\"" % (request.form.get("question_id"), i)
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "hints",
                "hint_number = %s" % (request.form.get("new_order")),
                "hint_id = \"%s\"" % (request.form.get("hint_id"))
            )
    

        # If the new order is higher than the old order 
        else:
            # Create a list of numbers from the old order to the new order.
            order = list(range(int(request.form.get("old_order")),int(request.form.get("new_order"))+1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "hints",
                "hint_number = 0",
                "hint_id = \"%s\"" % (request.form.get("hint_id"))
            )

            # This will shift all other orders down 1 from the "new order +1" to the "old order"
            for i in range(len(order)):
                update_db_entry(
                    "hints",
                    "hint_number = %s" % (order[i-1]),
                    "question_id = \"%s\" AND hint_number = \"%s\"" % (request.form.get("question_id"), order[i])
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "hints",
                "hint_number = %s" % (request.form.get("new_order")),
                "hint_id = \"%s\"" % (request.form.get("hint_id"))
            )

        # These three if/else statments will return the user back to the appropriate pages
        # If this function was called from the round edit page, then it'll return you to the round edit page
        return redirect(url_for(
            request.form.get("source_point")
        ),
            code = 307
        )
    
    else:
        return redirect(url_for(
            'home'
        ))  



# HOST     ############################################################################

# This will display an overview page showing all quizzes
@app.route('/host_a_quiz', methods=['GET', 'POST'])
def host_a_quiz():
    # Check to see if the user is an admin
    if admin_check():
        # This will return a dictionary of all quizzes with their quiz_id and quiz_name    
        upcoming_quiz_info = join_tables(
            "DISTINCT quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description", 
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE live.quiz_completed is NULL AND live.quiz_active is NULL AND live.quiz_id IS NOT NULL"
        )

        unassociated_quiz_info = compare_two_tables2(
            "quizzes",
            "live",
            "quiz_id"
        )

        active_quiz_info = join_tables(
            "DISTINCT quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description", 
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE live.quiz_completed is NULL AND live.quiz_active = 1"
        )

        completed_quiz_info = join_tables(
            "DISTINCT quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description", 
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE live.quiz_completed is not NULL AND live.quiz_active is NULL"
        )

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/host_a_quiz/host_a_quiz.html",
            name        = "Host a quiz",
            upcoming_quiz_info    = upcoming_quiz_info,
            completed_quiz_info   = completed_quiz_info,
            active_quiz_info      = active_quiz_info,
            unassociated_quiz_info = unassociated_quiz_info
        )

    else:
        return redirect(url_for(
            'home'
        )) 
    

# This function will use the quiz_id, round_id and question_id to display the host view for the current question
# This function will require work, now that a post form is the standard
@app.route('/host_live_quiz', methods=['GET', 'POST'])
def host_live_quiz():
    # Check to see if the user is an admin
    if admin_check() and request.method == 'POST':
        # Gets information on the current quiz based of the quiz_id
        quiz_info = common_value(
            "quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description, live.quiz_active, live.quiz_completed", 
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE quizzes.quiz_id = %s" % (request.form.get('quiz_id'))
        )

        # Collects information on all the rounds associated with the quiz
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.round_order, live.round_active, live.round_completed",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.quiz_id = %s" % (request.form.get('quiz_id'))
        )

        # Sorts the dictionaries of rounds in order of their round_order
        associated_round_info = sorted(associated_round_info, key=lambda k: k['round_order'])

        quiz_info['number_of_associated_rounds'] = len(associated_round_info)

        associated_questions = []
        for round in associated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_id, questions.question_tag, questions.question_correct_answer, questions.question_category_id, questions.question_scoring_type_id, questions.question_text, questions.question_difficulty, questions.question_points, live.question_order, live.question_active, live.question_completed, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (round['round_id'])
            )
            for associated_question in associated_question_info:
                associated_question['round_order'] = get_entry_from_db(
                    "round_order",
                    "live",
                    "round_id = \"%s\" AND quiz_id = \"%s\"" % (round['round_id'], request.form.get('quiz_id'))
                )['round_order']
                associated_questions.append(associated_question)

                if associated_question['question_correct_answer'] is not None:
                    clean_text, urls = detect_urls(associated_question['question_correct_answer'])
                    if urls:
                        associated_question['question_correct_answer'] = clean_text
                        associated_question['urls'] = urls
            
            round['number_of_associated_questions'] = len(associated_question_info)
            round['lock_answers'] = get_entry_from_db(
                    "lock_answers",
                    "live",
                    "round_id = \"%s\" AND quiz_id = \"%s\"" % (round['round_id'], request.form.get('quiz_id'))
                )['lock_answers']
            quiz_info['lock_answers'] = round['lock_answers']
            
            if associated_question_info:
                # Average question difficulty
                round['average_question_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                round['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    round['mode_question_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        round['mode_question_category'] = "Not set"
                        
                round['completed_questions'] = int(sum(1 for item in associated_question_info if "question_completed" in item and item["question_completed"] == 1))
                round['percentage_complete'] = int(sum(1 for item in associated_question_info if "question_completed" in item and item["question_completed"] == 1)/round['number_of_associated_questions']*100)

        # associated_questions = set(associated_questions)
        quiz_info['number_of_associated_questions'] = len(associated_questions)

        if associated_questions:
            # Number of questions in the quiz
            quiz_info['number_of_questions'] = len(associated_questions)
            # Average question difficulty
            quiz_info['average_question_difficulty'] = average(associated_questions, "question_difficulty")
            # Total question points
            quiz_info['total_points'] = total(associated_questions, "question_points")
            # Mode question category
            question_category_id = mode(associated_questions, "question_category_id")
            if question_category_id == []:
                quiz_info['mode_question_category'] = "None set"
            else:
                if len(question_category_id) > 1:
                    mode_question_categories = []
                    for question_category in question_category_id:
                        question_category_name = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category)
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    quiz_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    quiz_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (question_category_id[0])
                    )['category_name']
                else:
                    quiz_info['mode_question_category'] = "Not set"

            quiz_info['completed_questions'] = len(get_entries_from_db(
                "question_id",
                "live",
                "question_completed = 1"
            ))

            quiz_info['percentage_completed'] = int(int(quiz_info['completed_questions'])/int(quiz_info['number_of_questions'])*100)

        for round in associated_round_info:
            if round['round_active'] == 1:
                current_round_id = round['round_id']
                break
            else:
                current_round_id = 0
            if round['round_completed'] != 1 and quiz_info['quiz_active'] == 1:
                round['next_round'] = True
                break

        round_questions = common_values(
                "questions.question_id, questions.question_tag, questions.question_correct_answer, questions.question_category_id, questions.question_scoring_type_id, questions.question_text, questions.question_difficulty, questions.question_points, live.question_order, live.question_active, live.question_completed, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_active = 1"
            )
        
        answers = common_values(
            "users.username, users.user_id, answers.answer_text, answers.hints_used, answers.answer_timestamp, answers.question_id, answers.round_id, answers.answer_correct, answers.hints_used",
            "answers",
            "users",
            "answers.user_id",
            "users.user_id WHERE answers.quiz_id = \"%s\" AND answers.round_id = \"%s\"" % (quiz_info['quiz_id'], current_round_id)
        )
        answers = sorted(answers, key=lambda k: k['answer_timestamp'])

        # Sorts the dictionaries of rounds in order of their round_order
        round_questions = sorted(round_questions, key=lambda k: k['question_order'])

        if count(
            "live",
            "round_completed",
            "1 AND quiz_id = %s" % (request.form.get('quiz_id'))
        )[0] == len(associated_round_info):
            quiz_info['quiz_end'] = True

        if 'quiz_end' in quiz_info or quiz_info['quiz_completed'] is not None:
            round_questions = associated_questions
            answers = common_values(
                "users.username, users.user_id, answers.answer_text, answers.hints_used, answers.answer_timestamp, answers.question_id, answers.round_id, answers.answer_correct, answers.answer_points",
                "answers",
                "users",
                "answers.user_id",
                "users.user_id WHERE answers.quiz_id = \"%s\"" % (quiz_info['quiz_id'])
            )
            answers = sorted(answers, key=lambda k: k['answer_timestamp'])


        for question in round_questions:
            question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (question['question_category_id'])
                    )['category_name']
            
            if question['question_correct_answer'] is not None:
                clean_text, urls = detect_urls(question['question_correct_answer'])
                if urls:
                    question['question_correct_answer'] = clean_text
                    question['urls'] = urls
            
        for question in round_questions:
            question['question_scoring_type_name'] = get_entry_from_db(
                        "question_scoring_type_name",
                        "question_scoring_type",
                        "question_scoring_type_id = \"%s\"" % (question['question_scoring_type_id'])
                    )['question_scoring_type_name']
            
        for question in round_questions:
            question_media_info = get_entries_from_db(
                "*",
                "question_media",
                "question_id = \"%s\"" % (question['question_id'])
            )

            question['amount_of_media'] = len(get_entries_from_db(
                "question_media_id",
                "question_media",
                "question_id = \"%s\"" % (question['question_id'])
            ))
            

            for media in range(len(question_media_info)):
                question['media_%s_url' % (media)] = question_media_info[media]['question_media_url']
                question['media_%s_type' % (media)] = question_media_info[media]['question_media_type']
                question['media_%s_description' % (media)] = question_media_info[media]['question_media_description'] 
            
        for question in round_questions:
            if question['question_active'] == 1:
                break
            if question['question_completed'] != 1:
                question['next_question'] = True
                break

        for question in reversed(round_questions):
            if "next_question" in question or question['question_active']:
                break  # Stop searching if found
            elif quiz_info['quiz_active'] == True and question['question_completed']:  # Executed only if the loop completes without finding the key
                quiz_info['round_end'] = True


        # Returns information for which users are ready to start the quiz
        participant_info = common_values(
            "users.username, users.user_id, participants.participant_ready, participants.participant_score, participants.participant_position, participants.participant_item_id",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE quiz_id = %s" % (request.form.get('quiz_id'))
        )

        for participant in participant_info:
            if participant['participant_item_id']:
                participant['item_name'] = get_entry_from_db(
                            "item_name",
                            "items",
                            "item_id = \"%s\"" % (participant['participant_item_id'])
                        )['item_name']

        participant_info = sorted(participant_info, key=lambda k: k['participant_position'])

        if not count_not(
            "participants",
            "participant_ready",
            "1"
        )[0] > 0:
            quiz_info['quiz_ready'] = True


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/host_a_quiz/host_live_quiz.html",
            name                    = quiz_info['quiz_name'],
            quiz_info               = quiz_info,
            associated_round_info   = associated_round_info,
            round_questions         = round_questions,
            participant_info        = participant_info,
            answers                 = answers
        )
    
    else:
        flash("You can't just go straight to hosting the quiz")
        return redirect(url_for(
            'home'
        ))  
    
@app.route('/host_live_quiz/score', methods=['GET', 'POST'])
def score():
    # This will lable a quiz as active
    if admin_check() and request.method == "POST":
        for update in range(len(request.form.getlist('points'))):
            update_leaderboard(request.form.getlist('user_id')[update], request.form.getlist('quiz_id')[update], request.form.getlist('points')[update])
        return redirect(url_for(
            request.form.get('source_point')
        ),
            code = 307
        )
    
    else:
        flash("Pay me £20 and I will do this")
        return redirect(url_for(
            'home'
        ))

@app.route('/host_live_quiz/lock_answers', methods=['GET', 'POST'])
def lock_answers():
    # This will lable a quiz as active
    if admin_check() and request.method == "POST":
        update_db_entry(
            "live",
            "lock_answers = 1",
            "round_id = \"%s\" AND quiz_id = \"%s\"" % (request.form.get('round_id'), request.form.get('quiz_id'))
        )
        return redirect(url_for(
            request.form.get('source_point')
        ),
            code = 307
        )
    
    else:
        flash("Pay me £20 and I will do this")
        return redirect(url_for(
            'home'
        ))  

@app.route('/host_live_quiz/start_quiz', methods=['GET', 'POST'])
def start_quiz():
    # This will lable a quiz as active
    if admin_check() and request.method == "POST":
        if count_not("participants", "participant_ready", "1")[0] > 0:
            flash("Quiz not started, someone isn't ready")
            return redirect(url_for(
                'host_live_quiz'
            ),
                code = 307
            )
        
        else:
            flash("The Quiz has started!")
            # This updates the value of active to TRUE in the database for the quiz  
            update_db_entry(
                "live",
                "quiz_active = 1",
                "quiz_id = %s" % (request.form.get('quiz_id'))
            )

            # Redirects the user back to the host live quiz
            return redirect(url_for(
                'host_live_quiz'
            ),
                code = 307
            )
    
    else:
        flash("test")
        return redirect(url_for(
            'home'
        ))  

@app.route('/host_live_quiz/start_round', methods=['GET', 'POST'])
def start_round():
    # This will lable a quiz as active        
    if admin_check() and request.method == 'POST':
        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "round_active = 1",
            "round_id = %s" % (request.form.get('round_id'))
        )

        # Redirects the user back to the host live quiz
        return redirect(url_for(
            'host_live_quiz'
        ),
            code    = 307
        )
    
    # This is incase someone tries to be naughty
    else:
        flash("Naughty, naughty")
        return redirect(url_for(
            'home'
        ))  

# This will act also as end of round
@app.route('/host_live_quiz/start_question', methods=['GET', 'POST'])
def start_question():
    if admin_check() and request.method == 'POST':
        participants = get_entries_from_db(
            "user_id, participant_item_id",
            "participants",
            "quiz_id = %s" % (request.form.get('quiz_id'))
        )
        for participant in participants:
            if participant['participant_item_id'] is None:
                get_item(participant['user_id'], request.form.get('quiz_id'))

        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "question_active = 1",
            "question_id = %s" % (request.form.get('question_id'))
        )

        # Redirects the user back to the host live quiz
        return redirect(url_for(
            'host_live_quiz'
        ),
            code    = 307
        )
    
    # This is incase someone tries to be naughty
    else:
        flash("Naughty, naughty")
        return redirect(url_for(
            'home'
        )) 
    
@app.route('/host_live_quiz/complete_question', methods=['GET', 'POST'])
def complete_question():
    if admin_check() and request.method == 'POST':
        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "question_active = NULL, question_completed = 1",
            "question_id = %s" % (request.form.get('question_id'))
        )

        # update_db_entry(
        #     "participants",
        #     "participant_item_id = NULL",
        #     "quiz_id = \"%s\"" % (request.form.get('quiz_id'))
        # )

        # Redirects the user back to the host live quiz
        return redirect(url_for(
            'host_live_quiz'
        ),
            code    = 307
        )
    
    # This is incase someone tries to be naughty
    else:
        flash("Naughty, naughty")
        return redirect(url_for(
            'home'
        ))  

@app.route('/host_live_quiz/complete_round', methods=['GET', 'POST'])
def complete_round():
    if admin_check() and request.method == 'POST':
        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "round_active = NULL, round_completed = 1, lock_answers = NULL",
            "round_id = %s" % (request.form.get('round_id'))
        )

        update_db_entry(
            "participants",
            "participant_item_id = NULL",
            "quiz_id = \"%s\"" % (request.form.get('quiz_id'))
        )

        # This retrieves information about the answers in the round
        field_names = request.form.keys()
        dict={}
        for field_name in field_names:
            value = request.form.get(field_name)
            dict[field_name] = value

        # This will now update the answers table with the questions from the quiz
        list3=[]
        del dict['quiz_id']
        del dict['round_id']
        for key in dict:
            list2=[]
            list2.extend(key.split("-"))
            list3.append({"answer_correct":dict[key],"user_id":list2[0], "question_id":list2[-1], "round_id":str(request.form.get('round_id')), "quiz_id":str(request.form.get('quiz_id'))})
        
        for answer in list3:
            update_db_entry(
                "answers",
                "answer_correct = %s" % (answer["answer_correct"]),
                "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (answer['user_id'], answer['question_id'], answer['round_id'], answer['quiz_id'])
            )

        round_questions = common_values(
                "questions.question_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (request.form.get('round_id'))
            )

        for question in round_questions:
            mark_answer(
                question["question_id"],
                str(request.form.get('round_id')),
                str(request.form.get('quiz_id'))
            )

        # Returns information for which users are ready to start the quiz
        participant_info = common_values(
            "participants.user_id, answers.answer_points",
            "answers",
            "participants",
            "answers.user_id",
            "participants.user_id WHERE answers.round_id = \"%s\" AND participants.quiz_id = \"%s\"" % (request.form.get('round_id'), request.form.get('quiz_id'))
        )

        for participant in participant_info:
            update_leaderboard(participant['user_id'], request.form.get('quiz_id'), participant['answer_points'])
        

        # Redirects the user back to the host live quiz
        return redirect(url_for(
            'host_live_quiz'
        ),
            code    = 307
        )
    
    # This is incase someone tries to be naughty
    else:
        flash("Naughty, naughty")
        return redirect(url_for(
            'home'
        ))  

@app.route('/host_live_quiz/complete_quiz', methods=['GET', 'POST'])
def complete_quiz():
    if admin_check() and request.method == 'POST':
        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "quiz_active = NULL, quiz_completed = \"%s\"" % (timestamp()),
            "quiz_id = %s" % (request.form.get('quiz_id'))
        )

        # Redirects the user back to the host live quiz
        return redirect(url_for(
            'host_live_quiz'
        ),
            code    = 307
        )
    
    # This is incase someone tries to be naughty
    else:
        flash("Naughty, naughty")
        return redirect(url_for(
            'home'
        ))  


# JOIN     ############################################################################

# This function will display a web page with information about all the quizzes
@app.route('/join_a_quiz', methods=['GET', 'POST'])
def join_a_quiz():
    # Grabs information on all the quizzes
    active_quiz_info = common_values(
        "DISTINCT quizzes.quiz_id, quizzes.quiz_name, live.quiz_active",
        "quizzes",
        "participants",
        "quizzes.quiz_id",
        "participants.quiz_id INNER JOIN live on live.quiz_id = quizzes.quiz_id WHERE live.quiz_active = 1 AND participants.user_id = %s" % (session['user_id'])
    )

    upcoming_quiz_info = common_values(
        "DISTINCT quizzes.quiz_id, quizzes.quiz_name, live.quiz_active",
        "quizzes",
        "participants",
        "quizzes.quiz_id",
        "participants.quiz_id INNER JOIN live on live.quiz_id = quizzes.quiz_id WHERE live.quiz_active IS NULL AND live.quiz_completed IS NULL AND participants.user_id = %s" % (session['user_id'])
    )

    previous_quiz_info = common_values(
        "DISTINCT quizzes.quiz_id, quizzes.quiz_name",
        "quizzes",
        "participants",
        "quizzes.quiz_id",
        "participants.quiz_id INNER JOIN live on live.quiz_id = quizzes.quiz_id WHERE live.quiz_completed IS NOT NULL AND participants.user_id = %s" % (session['user_id'])
    )

    # Feeds data into HTML Jinja2 template
    return render_template(
        "quiz/join_a_quiz/join_a_quiz.html",
        name                = "Join a quiz",
        previous_quiz_info  = previous_quiz_info,
        upcoming_quiz_info  = upcoming_quiz_info,
        active_quiz_info    = active_quiz_info
    )

# This function will display the current active quiz, Round or Question information
#This will need fundamentally changed due to post being standardised now
@app.route('/live_quiz', methods=['GET', 'POST']) #maybe add user_id into app route
def live_quiz():
    # Check to see if the user is an admin
    if request.method == 'POST':
        # Gets information on the current quiz based of the quiz_id
        quiz_info = common_value(
            "quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description, live.quiz_active, live.quiz_completed", 
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE quizzes.quiz_id = %s" % (request.form.get('quiz_id'))
        )

        # Collects information on all the rounds associated with the quiz
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.round_order, live.round_active, live.round_completed",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.quiz_id = %s" % (request.form.get('quiz_id'))
        )

        # Sorts the dictionaries of rounds in order of their round_order
        associated_round_info = sorted(associated_round_info, key=lambda k: k['round_order'])

        quiz_info['number_of_associated_rounds'] = len(associated_round_info)

        associated_questions = []
        for round in associated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_id, questions.question_tag, questions.question_type_id, questions.question_correct_answer, questions.question_category_id, questions.question_scoring_type_id, questions.question_text, questions.question_difficulty, questions.question_points, live.question_order, live.question_active, live.question_completed, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = %s" % (round['round_id'])
            )
            for associated_question in associated_question_info:
                associated_question['round_order'] = get_entry_from_db(
                    "round_order",
                    "live",
                    "round_id = \"%s\" AND quiz_id = \"%s\"" % (round['round_id'], request.form.get('quiz_id'))
                )['round_order']
                associated_questions.append(associated_question)

                if associated_question['question_correct_answer'] is not None:
                    clean_text, urls = detect_urls(associated_question['question_correct_answer'])
                    if urls:
                        associated_question['question_correct_answer'] = clean_text
                        associated_question['urls'] = urls
            
            round['number_of_associated_questions'] = len(associated_question_info)

            if associated_question_info:
                # Average question difficulty
                round['average_question_difficulty'] = average(associated_question_info, "question_difficulty")
                # Total question points
                round['total_points'] = total(associated_question_info, "question_points")
                # Mode question category
                question_category_id = mode(associated_question_info, "question_category_id")
                if question_category_id == []:
                    round['mode_question_category'] = "None set"
                else:
                    if len(question_category_id) > 1:
                        mode_question_categories = []
                        for question_category in question_category_id:
                            question_category_name = get_entry_from_db(
                                "category_name",
                                "categories",
                                "category_id = \"%s\"" % (question_category)
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category_id[0])
                        )['category_name']
                    else:
                        round['mode_question_category'] = "Not set"

                round['completed_questions'] = int(sum(1 for item in associated_question_info if "question_completed" in item and item["question_completed"] == 1))
                round['percentage_complete'] = int(sum(1 for item in associated_question_info if "question_completed" in item and item["question_completed"] == 1)/round['number_of_associated_questions']*100)

        # associated_questions = set(associated_questions)
        quiz_info['number_of_associated_questions'] = len(associated_questions)

        if associated_questions:
            # Number of questions in the quiz
            quiz_info['number_of_questions'] = len(associated_questions)
            # Average question difficulty
            quiz_info['average_question_difficulty'] = average(associated_questions, "question_difficulty")
            # Total question points
            quiz_info['total_points'] = total(associated_questions, "question_points")
            # Mode question category
            question_category_id = mode(associated_questions, "question_category_id")
            if question_category_id == []:
                quiz_info['mode_question_category'] = "None set"
            else:
                if len(question_category_id) > 1:
                    mode_question_categories = []
                    for question_category in question_category_id:
                        question_category_name = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"%s\"" % (question_category)
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    quiz_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    quiz_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (question_category_id[0])
                    )['category_name']
                else:
                    quiz_info['mode_question_category'] = "Not set"
           
            quiz_info['completed_questions'] = len(get_entries_from_db(
                "question_id",
                "live",
                "question_completed = 1"
            ))

            quiz_info['percentage_completed'] = int(int(quiz_info['completed_questions'])/int(quiz_info['number_of_questions'])*100)

        for round in associated_round_info:
            if round['round_active'] == 1:
                break
            if round['round_completed'] != 1 and quiz_info['quiz_active'] == 1:
                round['next_round'] = True
                break

        round_questions = common_values(
                "questions.question_id, questions.question_correct_answer, questions.question_tag, questions.question_scoring_type_id, questions.question_type_id, questions.question_category_id, questions.question_difficulty, questions.question_points, questions.question_text, live.question_order, live.round_id, live.question_active, live.question_completed",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_active = 1"
            )
        

        # Sorts the dictionaries of rounds in order of their round_order
        round_questions = sorted(round_questions, key=lambda k: k['question_order'])

        if count(
            "live",
            "round_completed",
            "1 AND quiz_id = %s" % (request.form.get('quiz_id'))
        )[0] == len(associated_round_info):
            quiz_info['quiz_end'] = True

        if 'quiz_end' in quiz_info or quiz_info['quiz_completed'] is not None:
            round_questions = associated_questions

        for question in round_questions:
            if question['question_correct_answer'] is not None:
                clean_text, urls = detect_urls(question['question_correct_answer'])
                if urls:
                    question['question_correct_answer'] = clean_text
                    question['urls'] = urls

            if check_single_db(
                "answer_text",
                "answers",
                "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (session['user_id'], question['question_id'], question['round_id'], request.form.get('quiz_id'))
            ):
                answer_info = get_entry_from_db(
                    "answer_text, hints_used, answer_points",
                    "answers",
                    "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (session['user_id'], question['question_id'], question['round_id'], request.form.get('quiz_id'))
                )
                question['answer_text'] = answer_info['answer_text']
                question['answer_points'] = answer_info['answer_points']
                if answer_info['hints_used']:
                    question['hints_used'] = answer_info['hints_used']
                else:
                    question['hints_used'] = 0

                question['number_of_hints'] = len(get_entries_from_db(
                    "hint_id",
                    "hints",
                    "question_id = \"%s\"" % (question['question_id'])
                ))

                # Prevent divisible by zero error. Maybe find smarter way to fix this
                if question['number_of_hints'] != 0:
                    question['hint_cost'] = int((question['question_points']-1)/(question['number_of_hints']))

                    for hint in range(1,int(question['hints_used'])+1):
                        question['hint_%s' % (hint)] = get_entry_from_db(
                            "hint_text",
                            "hints",
                            "question_id = \"%s\" AND hint_number = \"%s\"" % (question['question_id'], hint)
                        )['hint_text']

            question_media_info = get_entries_from_db(
                "*",
                "question_media",
                "question_id = \"%s\"" % (question['question_id'])
            )

            question['amount_of_media'] = len(get_entries_from_db(
                "question_media_id",
                "question_media",
                "question_id = \"%s\"" % (question['question_id'])
            ))
            

            for media in range(len(question_media_info)):
                question['media_%s_url' % (media)] = question_media_info[media]['question_media_url']
                question['media_%s_type' % (media)] = question_media_info[media]['question_media_type']
                question['media_%s_description' % (media)] = question_media_info[media]['question_media_description']            

            question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"%s\"" % (question['question_category_id'])
            )['category_name']
            
            question['question_type'] = get_entry_from_db(
                "question_type_name",
                "question_type",
                "question_type_id = \"%s\"" % (question['question_type_id'])
            )['question_type_name']
            
            question['question_scoring_type'] = get_entry_from_db(
                        "question_scoring_type_name",
                        "question_scoring_type",
                        "question_scoring_type_id = \"%s\"" % (question['question_scoring_type_id'])
            )['question_scoring_type_name']
            
        for question in round_questions:
            if question['question_active'] == 1:
                break
            if question['question_completed'] != 1:
                question['next_question'] = True
                break

            question['lock_answers'] = get_entry_from_db(
                    "lock_answers",
                    "live",
                    "round_id = \"%s\" AND quiz_id = \"%s\"" % (question['round_id'], request.form.get('quiz_id'))
                )['lock_answers']

        for question in reversed(round_questions):
            if "next_question" in question or question['question_active']:
                break  # Stop searching if found
            elif quiz_info['quiz_active'] == True:  # Executed only if the loop completes without finding the key
                quiz_info['round_end'] = True

        # Returns information for which users are ready to start the quiz
        all_participant_info = common_values(
            "users.username, users.user_id, participants.participant_ready, participants.participant_position, participants.participant_score",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE quiz_id = %s" % (request.form.get('quiz_id')) 
        )

        participant_info = common_value(
            "users.username, users.user_id, participants.participant_ready, participants.participant_position, participants.participant_score, participants.participant_item_id",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE participants.quiz_id = %s AND participants.user_id = %s" % (request.form.get('quiz_id'), session['user_id'])
        )

        leaderboard = filter_data(all_participant_info, session['user_id'])
        if participant_info['participant_item_id']:
            item_info = get_entry_from_db(
                        "item_name, item_description, chance_forwards, chance_backwards, chance_use",
                        "items",
                        "item_id = \"%s\"" % (participant_info['participant_item_id'])
                    )
            participant_info['item_name'] = item_info['item_name']
            participant_info['item_description'] = item_info['item_description']
            participant_info['chance_forwards'] = item_info['chance_forwards']
            participant_info['chance_backwards'] = item_info['chance_backwards']
            participant_info['chance_use'] = item_info['chance_use']

        if not count_not(
            "participants",
            "participant_ready",
            "1"
        )[0] > 0:
            quiz_info['quiz_ready'] = True

        leaderboard = sorted(leaderboard, key=lambda k: k['participant_position'])

        if 'score' in session and participant_info['participant_score'] > session['score']:
            flash("You have gained %s points" % (int(participant_info['participant_score']) - int(session['score'])))
        elif 'score' in session and participant_info['participant_score'] < session['score']:
            flash("You have lost %s points" % (int(session['score']) - int(participant_info['participant_score'])))

        if 'position' in session and participant_info['participant_position'] != session['position']:
            flash("You have moved from %s to %s place" % (ordinal(session['position']), ordinal(participant_info['participant_position'])))

        if 'item' in session and session['item'] != participant_info['participant_item_id']:
            if participant_info['participant_item_id'] is None:
                flash("You have no items")
            else:
                item_name = get_entry_from_db(
                    "item_name",
                    "items",
                    "item_id = %s" % (participant_info['participant_item_id'])
                )['item_name']
                flash(f"You have gained a {item_name} item")

        session['score'] = participant_info['participant_score']
        session['position'] = participant_info['participant_position']
        session['item'] = participant_info['participant_item_id']

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/join_a_quiz/live_quiz.html",
            name                    = quiz_info['quiz_name'],
            quiz_info               = quiz_info,
            associated_round_info   = associated_round_info,
            round_questions         = round_questions,
            participant_info        = participant_info,
            all_participant_info    = all_participant_info,
            leaderboard             = leaderboard
        )
    
    else:
        flash("You can't just go straight to hosting the quiz")
        return redirect(url_for(
            'home'
        ))
    
@app.route('/live_quiz/use_hint', methods=['GET', 'POST'])
def use_hint():
    # This will lable a quiz as active
    if request.method == "POST":
        if request.form.get('hints_used') == 'None':
            hints_used = 0
        else:
            hints_used = request.form.get('hints_used')

        question_points = int(get_entry_from_db(
            "question_points",
            "questions",
            "question_id = %s" % (request.form.get('question_id'))
        )['question_points'])

        number_of_hints = len(get_entries_from_db(
            "hint_id",
            "hints",
            "question_id = %s" % (request.form.get('question_id'))
        ))

        update_db_entry(
            "answers",
            "hints_used = %s" % (int(hints_used)+1),
            "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (request.form.get('user_id'), request.form.get('question_id'), request.form.get('round_id'), request.form.get('quiz_id'))
        )

        update_leaderboard(
            request.form.get('user_id'),
            request.form.get('quiz_id'),
            -int((question_points-1)/(number_of_hints))
        )

        flash("You spent %s points to unlock a hint" % (int(question_points-1/(number_of_hints))))
        return redirect(url_for(
            request.form.get('source_point')
        ),
            code = 307
        )
    
    else:
        flash("Pay me £20 and I will do this")
        return redirect(url_for(
            'home'
        ))
    
@app.route('/live_quiz/use_item', methods=['GET', 'POST'])
def use_item():
    # This will lable a quiz as active
    if request.method == "POST":
        if check_single_db(
            "participant_item_id",
            "participants",
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (session['user_id'], request.form.get('quiz_id'))
        ):
            item_function(
                session['user_id'],
                request.form.get('quiz_id'),
                request.form.get('participant_item_id'),
                request.form.get('use')
            )
            update_db_entry(
                "participants",
                "participant_item_id = NULL",
                "user_id = \"%s\" AND quiz_id = \"%s\"" % (session['user_id'], request.form.get('quiz_id'))
            )
        else:
            flash("You lost the item")

        return redirect(url_for(
            request.form.get('source_point')
        ),
            code = 307
        )
    
    else:
        flash("Pay me £20 and I will do this")
        return redirect(url_for(
            'home'
        ))

# This function will update the DB to say that the user is ready to start the quiz
@app.route('/quiz_ready', methods=['GET', 'POST'])
def quiz_ready():
    if request.method == "POST":
        # Updates DB with participant_ready = 1
        update_db_entry(
            "participants",
            "participant_ready = 1",
            "user_id = \"%s\" AND quiz_id = \"%s\"" % (request.form.get('user_id'), request.form.get('quiz_id'))
        )

        # Redirects the user back to the Live quiz page
        return redirect(url_for(
            'live_quiz'
        ),
            code = 307
        )

# This function will update the DB to say that the user is no longer ready to start the quiz
@app.route('/quiz_unready', methods=['GET', 'POST'])
def quiz_unready():
    if request.method == "POST":
        if check_single_db(
            "quiz_active",
            "live",
            "quiz_active = 1"
        ):
            flash("The Quiz has already started")
        else:
            # Updates DB with Read = 0
            update_db_entry(
                "participants", 
                "participant_ready = 0", 
                "user_id = \"%s\" AND quiz_id = \"%s\"" % (request.form.get('user_id'), request.form.get('quiz_id'))
            )
            flash("Pre Quiz nerves are normal")

        # Redirects the user back to the Live quiz page
        return redirect(url_for(
            'live_quiz'
        ),
            code = 307
        )


# This function will submit the users answer the the answers table in the DB
@app.route('/submit_answer', methods=['GET','POST'])
def submit_answer():
    if request.method == "POST":
        if check_single_db(
            "lock_answers",
            "live",
            "lock_answers = \"1\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (request.form.get("round_id"), request.form.get("quiz_id"))
        ):
            flash("The Round has already ended. Your answer was not submitted")
        elif check_single_db(
            "question_active",
            "live",
            "(question_active = \"1\" OR question_completed = \"1\") AND question_id = \"%s\" AND round_id = \"%s\"" % (request.form.get("question_id"), request.form.get("round_id"))
        ):
            flash("Answer updated")
            # This checks if the user has already submitted an answer before
            if check_single_db(
                "user_id",
                "answers",
                "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (session['user_id'], request.form.get("question_id"), request.form.get("round_id"), request.form.get("quiz_id"))
            ):
                # This updates the Answers table with the new answer
                update_db_entry(
                    "answers",
                    "answer_text = \"%s\", answer_correct = NULL, answer_timestamp = \"%s\"" % (fix_string(request.form.get("new_answer")), timestamp()),
                    "user_id = \"%s\" AND question_id = \"%s\" AND round_id = \"%s\" AND quiz_id = \"%s\"" % (session['user_id'], request.form.get("question_id"), request.form.get("round_id"), request.form.get("quiz_id"))
                )

            # If this is the first answer being submitted
            else:
                # Insert the new answer into the table
                insert_db_entry(
                    "answers",
                    "user_id, question_id, round_id, quiz_id, answer_text, answer_timestamp",
                    "\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\"" % (session['user_id'], request.form.get("question_id"), request.form.get("round_id"), request.form.get("quiz_id"), fix_string(request.form.get("new_answer")), timestamp())
            )
        
        else:
            flash("You've jumped the gun! The question hasn't started yet. Your answer was not submitted")

        # Redirects user to the Live quiz page
        return redirect(url_for(
            'live_quiz'
        ),
            code = 307
        )

    else:
        flash("That wasn't submitted correctly")
        return redirect(url_for(
            'home'
        )) 


# Results     ############################################################################
# This will display a results page for a specific Quiz
@app.route('/all_results', methods=['GET','POST'])
def all_results():
    # Feeds data into HTML Jinja2 template
        # Returns information for which users are ready to start the quiz
        if session['user_admin'] == 0:
            quiz_info = join_tables(
                "DISTINCT quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description", 
                "quizzes",
                "live",
                "quizzes.quiz_id",
                "live.quiz_id INNER JOIN participants ON quizzes.quiz_id = participants.quiz_id WHERE live.quiz_completed is not NULL AND live.quiz_active is NULL AND participants.user_id = %s" % (session['user_id'])
            )
        else:
            quiz_info = join_tables(
                "DISTINCT quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description", 
                "quizzes",
                "live",
                "quizzes.quiz_id",
                "live.quiz_id WHERE live.quiz_completed is not NULL AND live.quiz_active is NULL"
            )


        return render_template(
            "quiz/results/all_results.html",
            name        = "Results",
            quiz_info   = quiz_info
        )


# This will display a results page for a specific Quiz
@app.route('/results', methods=['GET','POST'])
def results():
        # Returns information for which users participated in the quiz
        participant_info = common_values(
            "participants.participant_position, users.username, users.user_id, participants.participant_score",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE quiz_id = %s" % (request.form.get('quiz_id')) 
        )

        # Gets the name of the quiz
        quiz_info = get_entry_from_db(
                "quiz_name",
                "quizzes",
                "quiz_id = %s" % (request.form.get('quiz_id'))
            )

        participant_info = sorted(participant_info, key=lambda k: -k['participant_score'])

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/results/results.html",
            name                = "%s Results" % (quiz_info['quiz_name']),
            participant_info    = participant_info
        )

#######################################################################################################################################################################
# MISC.     ############################################################################
#######################################################################################################################################################################

# This will display the ts&cs page
@app.route('/t&c')
def terms_and_conditions():
    # Feeds data into HTML Jinja2 template
    return render_template(
        "misc/t_c.html",
        name = "T&Cs"
    )

# This will display the about us page
@app.route('/about')
def about():
    # Feeds data into HTML Jinja2 template
    return render_template(
        "misc/about.html",
        name = "About"
    )


#######################################################################################################################################################################
# RUN APP     ###########################################################################
#######################################################################################################################################################################

# This will run the app on the current hardware
if __name__ == "__main__":
    app.run(
        '0.0.0.0',
        debug = True
    )