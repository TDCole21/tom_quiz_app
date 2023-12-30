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
        if email(request.form.get('user_details')):
            login_via = "user_email"

        else:
            login_via = "username"

        # Checks if the username or Email exists in the users database
        if check_single_db(
            "user_id",
            "users",
            login_via + " = \"" + request.form.get('user_details') + "\""
        ):
            # Checks if the input password, when hashed, matches the one on the database
            if check_password_hash(
                get_entry_from_db(
                    "user_password",
                    "users",
                    login_via + " = \"" + request.form.get('user_details') + "\""
                )['user_password'],
                request.form.get('user_password')
            ):
                # Get user information
                account = get_entry_from_db(
                    "user_id, username, user_email, user_admin",
                    "users",
                    login_via + " = \"" + request.form.get('user_details') + "\""
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
            flash('register')     

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
            "username = \"" + session['username'] + "\""
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
            "user_email = \"" + request.form.get('new_user_email') + "\""
        ):
            flash('That email is already in use.')

        else:
            # Updates the database entry with the new email address
            update_db_entry(
                "users",
                "user_email = \"" + request.form.get('new_user_email') + "\"",
                "user_email = \"" + session['user_email'] + "\""
            )
            # Updates the session with the new email address
            session['user_email'] = request.form.get('new_user_email')

    # Redirects back to the profile page
    return redirect(url_for(
        'profile'
    ))

# Updates the user's username in the database and session
@app.route('/profile/username/update', methods=['GET', 'POST'])
def username_update():
    if request.method == "POST":
        # Checks is the username contains an @ symbol. I use the @ symbol to differentiate between user email and username
        if email(request.form.get('new_username')):
            flash('A username cannot contain an @ character.')

        # Checks if the new username already exists in the database
        elif check_single_db(
            "user_id",
            "users",
            "username = \"" + request.form.get('new_username')+"\""
        ):
            flash('That username is already in use.')

        else:
            # Updates the username entry in the database with the new username, using the session email as the identifier
            update_db_entry(
                "users",
                "username = \"" + request.form.get('new_username')+"\"",
                "username = \"" + session['username'] + "\""
            )
            # Updates the session with the new username
            session['username'] = request.form.get('new_username')

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
            "user_password = \"" + generate_password_hash(request.form.get('new_user_password'), method='pbkdf2') + "\"",
            "user_email = \"" + session['user_email'] + "\""
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
        if email(request.form.get('username')):
            flash('Signup failed. A username cannot contain an @ character.')

        # Checks is the username or email already exists in the database
        elif check_single_db(
            "user_id",
            "users",
            "username = \"" + request.form.get('username') + "\" OR user_email = \"" + request.form.get('user_email') + "\""
        ):
            flash('That account is already in use.')
            flash('login')

        else:
            # checks if the password and repeat password are the same
            if duplicate(
                request.form.get('user_password'),
                request.form.get('user_password_repeat')
            ):
                # Inserts the new values into the users table in the database. By default the user is not an admin (admin=0)
                insert_db_entry(
                    "users",
                    "username, user_email, user_password, user_admin",
                    "\"" + request.form.get('username') + "\", \"" + request.form.get('user_email') + "\", \"" + generate_password_hash(request.form.get('user_password'), method='pbkdf2') + "\", 0"
                )

                # This then grabs the information that was just entered into the database
                account = get_entry_from_db(
                    "user_id, username, user_email, user_admin",
                    "users",
                    "user_email = \"" + request.form.get('user_email') + "\""
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
                "live.round_id WHERE live.quiz_id = " + str(quiz['quiz_id'])
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
                    "live.question_id WHERE live.round_id = " + str(round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        quiz['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        quiz['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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
            "quiz_name = \"" + request.form.get('quiz_name') + "\""
        ):
            # Redirects user to the quiz maker/editor page
            flash('The quiz name, \"' + request.form.get('quiz_name') + '\", is already in use.')
            return redirect(url_for(
                'quiz_maker'
            ))

        else:
            # Creates a new entry in the quiz table using the quiz name form the form
            insert_db_entry(
                "quizzes",
                "quiz_name",
                "\"" + request.form.get('quiz_name') + "\""
            )

            # # Gets information about the newly created quiz
            # quiz_info = get_entry_from_db(
            #     "quiz_id",
            #     "quizzes",
            #     "quiz_name = \"" + request.form.get('quiz_name') + "\""
            # )

            # Redirects user to the quiz template page for the newly created quiz
            flash('The Quiz, \"' + str(request.form.get('quiz_name')) + '\", was successfully created.')
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
            "quiz_id = " + request.form.get('quiz_id')
        ):
            flash("This quiz does not exist")
            return redirect(url_for(
                'home'
            ))

        else:
            # Removes the quiz from the database based off the quiz_id
            delete_db_entry(
                "quizzes",
                "quiz_id = " + request.form.get('quiz_id')
            )

            # Redirects the user to the quiz Maker/Editor page
            flash ("The Quiz, \"" + request.form.get('quiz_name') + "\", has been deleted")
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
        insert_db_entry(
            "items",
            "item_name, item_description",
            "\"" + request.form.get('item_name') + "\", \"" + request.form.get('item_description') + "\""
        )
        flash("Item " + request.form.get('item_name') + " created")
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
        update_db_entry(
            "items",
            "item_name = \"" + request.form.get('new_item_name') + "\", item_description = \"" + request.form.get('new_item_description') + "\"",
            "item_name = \"" + request.form.get('old_item_name') + "\""
        )
        flash("Item " + request.form.get('old_item_name') + " updated to " + request.form.get('new_item_name'))
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
            "participant_item_id = \"" + request.form.get('participant_item_id') + "\""
        )
        delete_db_entry(
            "items",
            "item_name = \"" + request.form.get('item_name') + "\""
        )
        flash("Item " + request.form.get('item_name') + " deleted")
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
            "\"" + request.form.get('category_name') + "\", \"" + request.form.get('category_description') + "\""
        )
        flash("Category " + request.form.get('category_name') + " created")
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
            "category_name = \"" + request.form.get('new_category_name') + "\", category_description = \"" + request.form.get('new_category_description') + "\"",
            "category_name = \"" + request.form.get('old_category_name') + "\""
        )
        flash("Category " + request.form.get('old_category_name') + " updated to " + request.form.get('new_category_name'))
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
            "question_category_id = \"" + request.form.get('category_id') + "\""
        )
        delete_db_entry(
            "categories",
            "category_name = \"" + request.form.get('category_name') + "\""
        )
        flash("Category " + request.form.get('category_name') + " deleted")
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
            "\"" + request.form.get('question_type_name') + "\", \"" + request.form.get('question_type_description') + "\""
        )
        flash("Question type " + request.form.get('question_type_name') + " created")
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
            "question_type_name = \"" + request.form.get('new_question_type_name') + "\", question_type_description = \"" + request.form.get('new_question_type_description') + "\"",
            "question_type_name = \"" + request.form.get('old_question_type_name') + "\""
        )
        flash("Question type " + request.form.get('old_question_type_name') + " updated to " + request.form.get('new_question_type_name'))
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
            "question_type_id = \"" + request.form.get('question_type_id') + "\""
        )
        delete_db_entry(
            "question_type",
            "question_type_name = \"" + request.form.get('question_type_name') + "\""
        )
        flash("Question type " + request.form.get('question_type_name') + " deleted")
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
            "\"" + request.form.get('question_scoring_type_name') + "\", \"" + request.form.get('question_scoring_type_description') + "\""
        )
        flash("Question scoring type " + request.form.get('question_scoring_type_name') + " created")
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
            "question_scoring_type_name = \"" + request.form.get('new_question_scoring_type_name') + "\", question_scoring_type_description = \"" + request.form.get('new_question_scoring_type_description') + "\"",
            "question_scoring_type_name = \"" + request.form.get('old_question_scoring_type_name') + "\""
        )
        flash("Question scoring type " + request.form.get('old_question_scoring_type_name') + " updated to " + request.form.get('new_question_scoring_type_name'))
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
            "question_scoring_type_id = \"" + request.form.get('question_scoring_type_id') + "\""
        )
        delete_db_entry(
            "question_scoring_type",
            "question_scoring_type_name = \"" + request.form.get('question_scoring_type_name') + "\""
        )
        flash("Question scoring type " + request.form.get('question_scoring_type_name') + " deleted")
        return redirect(url_for(
                request.form.get('source_point')
            ))
    else:
        flash("Please use the forms on the website")
        # Redirects user to the quiz Maker/Editor page
        return redirect(url_for(
            'home'
        ))
    
@app.route('/associate_round', methods=['GET', 'POST'])
def associate_round():
    if request.method == "POST":
        # Need to find how many rounds are in the quiz
        number_of_associated_rounds = get_entries_from_db(
            "round_id",
            "live",
            "quiz_id = \"" + request.form.get('quiz_id') + "\" AND round_id IS NOT NULL"
        )

        unique_associated_rounds = set()
        for associated_round in number_of_associated_rounds:
            unique_associated_rounds.add(associated_round["round_id"])

        number_of_associated_rounds = len(unique_associated_rounds)+1

        insert_db_entry(
            "live",
            "quiz_id, round_id, round_order",
            request.form.get('quiz_id') + ", " + request.form.get('round_id') + ", " + str(number_of_associated_rounds)
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
            "quiz_id = \"" + request.form.get('quiz_id') + "\" AND round_id = \"" + request.form.get('round_id') + "\""
        )

        # Need to find how many rounds are in the quiz
        number_of_associated_rounds = get_entries_from_db(
            "round_id",
            "live",
            "quiz_id = \"" + request.form.get('quiz_id') + "\" AND round_id IS NOT NULL"
        )

        unique_associated_rounds = set()
        for associated_round in number_of_associated_rounds:
            unique_associated_rounds.add(associated_round["round_id"])

        number_of_associated_rounds = len(unique_associated_rounds) +1

        # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
        for i in range(int(request.form.get('round_order')), number_of_associated_rounds):
            update_db_entry(
                "live",
                "round_order = " + str(i),
                "quiz_id = \"" + request.form.get('quiz_id') + "\" AND round_order = \"" + str(i+1) + "\""
            )

        flash("Round " + request.form.get('round_name') + " removed from Quiz")
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
            "question_id = \"" + request.form.get('question_id') + "\""
        )

        number_of_associated_hints=len(number_of_associated_hints)+1

        insert_db_entry(
            "hints",
            "question_id, hint_text, hint_number",
            "\"" + request.form.get('question_id') + "\", \"" + request.form.get('hint_text') + "\", \"" + str(number_of_associated_hints) + "\""
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
            "hint_text = \"" + request.form.get('hint_text') + "\"",
            "hint_id = \"" + request.form.get('hint_id') + "\""
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
            "hint_id = \"" + request.form.get('hint_id') + "\""
        )

        # Need to find how many rounds are in the quiz
        number_of_associated_hints = get_entries_from_db(
            "hint_id",
            "hints",
            "question_id = \"" + request.form.get('question_id') + "\""
        )

        number_of_associated_hints = len(number_of_associated_hints) +1

        # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
        for i in range(int(request.form.get('hint_number')), number_of_associated_hints):
            update_db_entry(
                "hints",
                "hint_number = " + str(i),
                "question_id = \"" + request.form.get('question_id') + "\" AND hint_number = \"" + str(i+1) + "\""
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
                "live.quiz_id WHERE live.round_id = " + str(round['round_id'])
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
                "live.question_id WHERE live.round_id = " + str(round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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

# # This will create a new Round that is related to a specific quiz
# @app.route('/create_round', methods=['GET', 'POST'])
# def create_associated_round():
#     # Check to see if the user is an admin
#     if admin_check() and request.method == "POST":

#         # Checks to see if the quiz exists  
#         if not check_single_db(
#             "quiz_id",
#             "quizzes",
#             "quiz_id = " + request.form.get('quiz_id')
#         ):
#             flash("This quiz does not exist")
#             # Redirects user to the quiz Maker/Editor page
#             return redirect(url_for(
#                 'quiz_maker'
#             ))

#         # Checks if there isn't already a round with the same name in the current quiz
#         # Why not allow two rounds in a quiz with the same name??
#         elif check_multiple_db(
#             "rounds.round_id",
#             "rounds",
#             "live",
#             "rounds.round_id",
#             "live.round_id INNER JOIN quizzes ON live.quiz_id = quizzes.quiz_id"
#         ):
#             flash("The Round name: " + request.form.get('round_name') + ", already exists in this quiz")
#             return redirect(url_for(
#                 request.form.get("source_point")+'_template'
#             ),
#                 code = 307
#             )

#         else:
#             # Calculates the number of Round for a given quiz_id
#             no_of_rounds = len(get_entries_from_db(
#                 "round_id",
#                 "live",
#                 "quiz_id = " + request.form.get('quiz_id')
#             ))

#             # Inserts the Round into the rounds table, using the no_of_rounds +1 as its unique identifier
#             insert_db_entry(
#                 "rounds",
#                 "round_name, round_order",
#                 "\"" + request.form.get('round_name') + "\", " + str(no_of_rounds + 1)
#             )

#             round_id = get_latest()[0]

#             # Retrieves the new Round information from the rounds table, using the no_of_rounds +1 as its unique identifier
#             round_info = get_entry_from_db(
#                 "round_id, round_order, round_name",
#                 "rounds",
#                 "round_id = " + str(round_id)
#             )

#             # Inserts the Round into the live table
#             insert_db_entry(
#                 "live",
#                 "quiz_id, round_id",
#                 request.form.get('quiz_id') + ", " + str(round_info["round_id"])
#             )
            
#             # Redirects users to the Round template html page, specific to the Round just created
#             flash("Round " + str(round_info['round_order']) + ": " + str(round_info['round_name']) + ", created")            
#             return redirect(url_for(
#                 request.form.get("source_point")+'_template'
#             ),
#                 code = 307
#             )

#     else:
#         flash("You either aren't authorised to create a round, or you tried to do it via unofficial means")
#         return redirect(url_for(
#             'home'
#         ))

# This will create a new Round
@app.route('/create_new_round', methods=['GET', 'POST'])
def create_new_round():
    # Check to see if the user is an admin
    if admin_check() and request.method == "POST":
            # Inserts the Round into the rounds table, using the no_of_rounds +1 as its unique identifier
            insert_db_entry(
                "rounds",
                "round_name",
                "\"" + request.form.get('round_name') + "\""
            )

            # Retrieves the new Round information from the rounds table, using the no_of_rounds +1 as its unique identifier
            # round_info = get_entry_from_db(
            #     "round_id, round_name",
            #     "rounds",
            #     "round_id is NOT NULL"
            # )

            # round_info = common_values(
            #     "rounds.round_id, rounds.round_name, live.quiz_id, live.question_id, live.question_order, live.round_order",
            #     "rounds",
            #     "live",
            #     "round_id",
            #     "round_id"
            # )

            

            
            # Redirects users to the Round template html page, specific to the Round just created
            flash("Round " + str(request.form.get('round_name')) + ", created")            
            return redirect(url_for(
                "round_maker"
            ))

    else:
        flash("You either aren't authorised to create a round, or you tried to do it via unofficial means")
        return redirect(url_for(
            'home'
        ))


# # This function will delete a round from the database, based on the Round id.
# @app.route('/delete_round', methods=['GET', 'POST'])
# def delete_round():
#     # Check to see if the user is an admin
#     if admin_check() and request.method == "POST":
#         # Retrieves the Round information from the rounds table based on the round_id
#         round_info = get_entry_from_db(
#             "quiz_id, round_order, round_name",
#             "rounds",
#             "round_id = " + request.form.get('round_id')
#         )

#         # Deletes the Round from the rounds table in the database based off the round_id
#         delete_db_entry(
#             "rounds",
#             "round_id = " + request.form.get('round_id')
#         )

#         # Calculates the number of rounds for a given quiz_id
#         no_of_rounds = len(get_entries_from_db(
#             "round_id",
#             "rounds",
#             "quiz_id = "+ str(round_info['quiz_id'])
#         ))

#         # For all other rounds with round_orders greater than the one that was deleted, their round_order is reduced by one
#         for i in range(round_info['round_order'], no_of_rounds + 1):
#             update_db_entry(
#                 "rounds",
#                 "round_order = " + str(i),
#                 "round_order = " + str(i+1)
#             )

#         # Redirects users to the quiz template based on the quiz_id
#         flash("Round " + str(round_info['round_order']) + ": " + str(round_info['round_name']) + ", deleted")
#         return redirect(url_for(
#             request.form.get("source_point")
#         ),
#             code = 307
#         )
    
#     else:
#         flash("Something didn't go as planned")
#         return redirect(url_for(
#             'home'
#         ))

# This function will delete a round from the database, based on the Round id.
@app.route('/delete_round', methods=['GET', 'POST'])
def delete_round():
    # Check to see if the user is an admin
    if admin_check() and request.method == "POST":
        # This finds out all the live table entries involving the round
        associated_quizzes = get_entries_from_db(
            "quiz_id",
            "live",
            "round_id = \"" + request.form.get('round_id') + "\""
        )

        round_name = get_entry_from_db(
            "round_name",
            "rounds",
            "round_id = \"" + request.form.get('round_id') + "\""
        )

        unique_associated_quizzes_id = set()
        for associated_quiz in associated_quizzes:
            unique_associated_quizzes_id.add(associated_quiz["quiz_id"])

        unique_associated_quizzes = []
        for unique_associated_quiz in unique_associated_quizzes_id:
            all_unique_associated_quizzes = get_entry_from_db(
                "quiz_id, round_order",
                "live",
                "quiz_id = \"" + str(unique_associated_quiz) + "\" AND round_id = \"" + request.form.get('round_id') + "\""
            )
            unique_associated_quizzes.append(all_unique_associated_quizzes)


        # Deletes the Round from the rounds table in the database based off the round_id
        delete_db_entry(
            "rounds",
            "round_id = \"" + request.form.get('round_id') + "\""
        )

        # This if statement doesn't work
        if unique_associated_quizzes is not None:
            for quiz in unique_associated_quizzes:
                # Need to find how many rounds are in the quiz
                number_of_associated_rounds = get_entries_from_db(
                    "round_id",
                    "live",
                    "quiz_id = \"" + str(quiz['quiz_id']) + "\""
                )

                unique_associated_rounds = set()
                for associated_round in number_of_associated_rounds:
                    unique_associated_rounds.add(associated_round["round_id"])

                number_of_associated_rounds = len(unique_associated_rounds) +1

                # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
                for i in range(int(quiz['round_order']), number_of_associated_rounds):
                    update_db_entry(
                        "live",
                        "round_order = " + str(i),
                        "quiz_id = \"" + str(quiz['quiz_id']) + "\" AND round_order = \"" + str(i+1) + "\""
                    )


        # Redirects users to the quiz template based on the quiz_id
        flash("Round " + str(round_name['round_name']) + ", deleted")
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
                    "category_id = " + str(question['question_category_id'])
                )

                question['question_category']=question_category['category_name']

            associated_rounds = []
            # Collects information on all the quizzes this round is associated with
            associated_round_info = common_values(
                "rounds.round_name, rounds.round_id",
                "rounds",
                "live",
                "rounds.round_id",
                "live.round_id WHERE live.question_id = " + str(question['question_id'])
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
                    "live.quiz_id WHERE live.round_id = " + str(round['round_id'])
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

# This will create a Question associated with a specific Round
# @app.route('/create_new_question', methods=['GET', 'POST'])
# def create_new_question():

#     if admin_check() and request.method == "POST":
#         # Calculates the number of questions for a given round_id
#         no_of_questions = len(get_entries_from_db(
#             "question_id",
#             "questions",
#             "round_id = " + request.form.get('round_id')
#         ))

#         # Creates a new Question in the database, using the no_of_questions for the Question Order
#         insert_db_entry(
#             "questions",
#             "round_id, question_order, question_tag",
#             request.form.get('round_id') + ", " + str(1 + no_of_questions) + ", \"Question " + str(1 + no_of_questions) + "\""
#         )

#         # Retrieves the Question information from the database for the Question just created
#         question_info = get_entry_from_db(
#             "question_id, question_order",
#             "questions",
#             "round_id = " + request.form.get('round_id') + " AND question_order = " + str(1 + no_of_questions)
#         )

#         # Retrieves Round info for the flash message
#         round_info = get_entry_from_db(
#             "round_order, round_name",
#             "rounds",
#             "round_id = " + request.form.get('round_id')
#         )

#         # Redirects user to the Question template for the newly created Question
#         flash("Question " + str(question_info['question_order']) + " created in Round " + str(round_info['round_order']) + ": " + str(round_info['round_name']))
#         return redirect(url_for(
#             request.form.get("source_point")+'_template'
#         ),
#             code = 307
#         )
    
#     else:
#         return redirect(url_for(
#             'home'
#         ))

# Creates a question not associated to any quiz or round
@app.route('/create_new_question', methods=['GET', 'POST'])
def create_new_question():

    if admin_check() and request.method == "POST":
        # Creates a new Question in the database, using the no_of_questions for the Question Order
        insert_db_entry(
            "questions",
            "question_tag, question_type_id, question_category_id, question_points, question_scoring_type_id, question_difficulty",
            "\"" + request.form.get('question_tag') + "\", 1, 1,10, 1, 5 "
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


# This will delete a specific question, and depending on the page where it was actioned, will return the user to the appropriate page
# Editing! This is needs editing to allow for questions to be onipotent
# @app.route('/delete_question', methods=['GET', 'POST'])
# def delete_question():

#     if admin_check() and request.method == "POST":
#         # Retreives Question information based on the question_id, before the question is deleted.
#         question_info = get_entry_from_db(
#             "round_id, question_order",
#             "questions",
#             "question_id = " + request.form.get('question_id')
#         )
    
#         round_info = get_entry_from_db(
#             "round_order",
#             "rounds",
#             "round_id = " + str(question_info['round_id'])
#         )

#         # Calculates the number of questions for a given Round
#         no_of_questions = len(get_entries_from_db(
#             "question_id",
#             "questions",
#             "round_id = " + str(question_info['round_id'])
#         ))

#         # Removes the Question from the questions table in the database
#         delete_db_entry(
#             "questions",
#             "question_id = " + request.form.get('question_id')
#         )


#         # Not entering this if statement
#         if no_of_questions >1:
#             no_of_questions = no_of_questions-1

#             # Updates all other Question orders for that Round
#             for i in range(question_info['question_order'], no_of_questions + 1):
#                 update_db_entry(
#                     "questions",
#                     "question_order = " + str(i),
#                     "question_order = " + str(i+1)
#                 )

#         flash("Question " + str(question_info['question_order']) + " from Round " +  str(round_info['round_order']) + ", deleted")
#         return redirect(url_for(
#             request.form.get("source_point")+'_template'
#         ),
#             code = 307
#         )


#     else:
#         return redirect(url_for(
#             'home'
#         ))

@app.route('/delete_question', methods=['GET', 'POST'])
def delete_question():

    if admin_check() and request.method == "POST":
        # This finds out all the live table entries involving the round
        associated_rounds = get_entries_from_db(
            "round_id",
            "live",
            "question_id = \"" + request.form.get('question_id') + "\""
        )

        unique_associated_rounds_id = set()
        for associated_round in associated_rounds:
            unique_associated_rounds_id.add(associated_round["round_id"])

        unique_associated_rounds = []
        for unique_associated_round in unique_associated_rounds_id:
            all_unique_associated_rounds = get_entry_from_db(
                "round_id, question_order",
                "live",
                "round_id = \"" + str(unique_associated_round) + "\" AND question_id = \"" + request.form.get('question_id') + "\""
            )
            unique_associated_rounds.append(all_unique_associated_rounds)

        # Removes the Question from the questions table in the database
        delete_db_entry(
            "questions",
            "question_id = " + request.form.get('question_id')
        )

        if unique_associated_rounds is not None:
            for round in unique_associated_rounds:
                # Need to find how many rounds are in the quiz
                number_of_associated_questions = get_entries_from_db(
                    "question_id",
                    "live",
                    "round_id = \"" + str(round['round_id']) + "\""
                )

                unique_associated_questions = set()
                for associated_question in number_of_associated_questions:
                    unique_associated_questions.add(associated_question["question_id"])

                number_of_associated_questions = len(unique_associated_questions) +1

                # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
                for i in range(int(round['question_order']), number_of_associated_questions):
                    update_db_entry(
                        "live",
                        "question_order = " + str(i),
                        "round_id = \"" + str(round['round_id']) + "\" AND question_order = \"" + str(i+1) + "\""
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
        # Need to find how many rounds are in the quiz
        associated_questions = get_entries_from_db(
            "question_id",
            "live",
            "round_id = \"" + request.form.get('round_id') + "\" AND question_id IS NOT NULL"
        )

        unique_associated_questions = set()
        for associated_question in associated_questions:
            unique_associated_questions.add(associated_question["question_id"])

        number_of_associated_questions = len(unique_associated_questions)+1

        insert_db_entry(
            "live",
            "round_id, question_id, question_order",
            request.form.get('round_id') + ", " + request.form.get('question_id') + ", " +str(number_of_associated_questions)
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
            "question_id = \"" + request.form.get('question_id') + "\" AND round_id = \"" + request.form.get('round_id') + "\""
        )

        # Need to find how many questions are in the round
        number_of_associated_questions = get_entries_from_db(
            "question_id",
            "live",
            "round_id = \"" + request.form.get('round_id') + "\" AND question_id IS NOT NULL"
        )

        unique_associated_questions = set()
        for associated_question in number_of_associated_questions:
            unique_associated_questions.add(associated_question["question_id"])

        number_of_associated_questions = len(unique_associated_questions) +1

        # For all other rounds with round_orders greater than the one that was removed, their round_order is reduced by one
        for i in range(int(request.form.get('question_order')), number_of_associated_questions):
            update_db_entry(
                "live",
                "question_order = " + str(i),
                "round_id = \"" + request.form.get('round_id') + "\" AND question_order = \"" + str(i+1) + "\""
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
# Hints
@app.route('/add_question_media', methods=['GET', 'POST'])
def add_question_media():
    if request.method == "POST":
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
                "user_id, quiz_id",
                i + ", " + request.form.get('quiz_id')
            )

        return redirect(url_for(
            request.form.get("source_point")+'_template'
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
                "username = \"" + i + "\""
            )

            # Delete the user into the participants table
            delete_db_entry(
                "participants",
                "user_id = " + str(user_info['user_id']) + " AND quiz_id = " + request.form.get('quiz_id')
            )

        # Redirect user to the quiz template page for the current quiz
        return redirect(url_for(
            request.form.get("source_point")+'_template'
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
            "quiz_id = \"" + request.form.get('quiz_id') + "\""
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
            "quiz_id = \"" + request.form.get('quiz_id') + "\""
        )

        # Collects information on all the rounds associated with the quiz
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.round_order",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.quiz_id = " + request.form.get('quiz_id')
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
                "live.question_id WHERE live.round_id = " + str(round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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
                            "category_id = \"" + str(question_category) + "\""
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    quiz_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    quiz_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(question_category_id[0]) + "\""
                    )['category_name']
                else:
                    quiz_info['mode_question_category'] = "Not set"


        # This finds all the rounds not currentlu associated with the current quiz
        unassociated_round_info = compare_two_tables(
            "round_id, round_name, round_description",
            "rounds",
            "round_id",
            "live",
            "quiz_id = \"" + request.form.get('quiz_id') + "\""
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
                "live.question_id WHERE live.round_id = " + str(round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
                        )['category_name']
                    else:
                        round['mode_question_category'] = "Not set"


        # Returns all users who aren't already in the participant table
        user_info = compare_two_tables(
            "username, user_id",
            "users",
            "user_id",
            "participants",
            "quiz_id = \"" + request.form.get('quiz_id') +"\""
        )

        # Returns all users from the participant table, whilst grabbing their associated username from the users table
        participant_info = common_values_not_unique(
            "username",
            "users",
            "user_id",
            "participants",
            "quiz_id = \"" + request.form.get('quiz_id') + "\""
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
            "quiz_name = \"" + request.form.get('new_quiz_name') + "\""
        ):
            # If the quiz name is already in use, then the quiz name is not updated
            flash('That quiz name is already in use.')

        else:
            # If unqiue, then the quiz Name is updated
            update_db_entry(
                "quizzes",
                "quiz_name = \"" + request.form.get('new_quiz_name') + "\"",
                "quiz_id = " + request.form.get('quiz_id')
            )
            flash('Quiz name updated to ' + request.form.get('new_quiz_name'))

        # Redirects user to quiz template 
        return redirect(url_for(
            request.form.get("source_point")+'_template'
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
            "quiz_description = \"" + request.form.get('new_quiz_description').replace("\"", "") + "\"",
            "quiz_id = " + str(request.form.get('quiz_id')) #Is str needed?
        )

        # Redirects user to quiz template 
        flash('Quiz description updated')
        return redirect(url_for(
            request.form.get("source_point")+'_template'
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
            "round_id = " + str(request.form.get('round_id'))
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
            "round_id = \"" + request.form.get('round_id') + "\""
        )

        # Collects information on all the quizzes this round is associated with
        associated_quiz_info = common_values(
            "quizzes.quiz_id, quizzes.quiz_name, quizzes.quiz_description, live.round_order",
            "quizzes",
            "live",
            "quizzes.quiz_id",
            "live.quiz_id WHERE live.round_id = " + request.form.get('round_id')
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
                "live.round_id WHERE live.quiz_id = " + str(quiz['quiz_id'])
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
                    "live.question_id WHERE live.round_id = " + str(round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        quiz['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        quiz['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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
                "live.round_id WHERE live.quiz_id = " + str(quiz['quiz_id'])
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
                    "live.question_id WHERE live.round_id = " + str(round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        quiz['mode_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        quiz['mode_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
                        )['category_name']
                    else:
                        quiz['mode_category'] = "Not set"
        

        # Collects information on all the quizzes this round is associated with
        associated_question_info = common_values(
            "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_points, questions.question_difficulty, live.question_order, live.round_id",
            "questions",
            "live",
            "questions.question_id",
            "live.question_id WHERE live.round_id = " + request.form.get('round_id')
        )

        if associated_question_info:
            for associated_question in associated_question_info:
                associated_round_names =[]
                associated_question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(associated_question['question_category_id']) + "\""
                    )['category_name']
                
                associated_round_info = common_values(
                    "rounds.round_name",
                    "rounds",
                    "live",
                    "rounds.round_id",
                    "live.round_id WHERE live.question_id = " + str(associated_question['question_id'])
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
                            "category_id = \"" + str(question_category) + "\""
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    round_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    round_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(question_category_id[0]) + "\""
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
                        "category_id = \"" + str(unassociated_question['question_category_id']) + "\""
                    )['category_name']
                
                associated_round_info = common_values(
                    "rounds.round_name",
                    "rounds",
                    "live",
                    "rounds.round_id",
                    "live.round_id WHERE live.question_id = " + str(unassociated_question['question_id'])
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

        # Uses an Inner Join to get all information required of the round
        # round_info = get_values(
        #     "one",
        #     "SELECT "
        #         "rounds.round_id, rounds.round_name, rounds.round_order, rounds.round_description,"
        #         "quizzes.quiz_id, quizzes.quiz_name "
        #     "FROM ("
        #         "rounds INNER JOIN quizzes ON rounds.quiz_id = quizzes.quiz_id) "
        #     "WHERE "
        #         "rounds.round_id = " + request.form.get('round_id') + ";"    
        # )

        # # Using the round_id, it retrieves information about the all the questions associtate with the Round
        # question_info = get_entries_from_db(
        #     "question_id, question_order, question_tag",
        #     "questions",
        #     "round_id = " + request.form.get('round_id')
        # )
        # # Sorts the dictionaries of questions in order of their question_order
        # question_info = sorted(question_info, key=lambda k: k['question_order']) 

        # # Calculates the number of rounds in the quiz
        # number_of_rounds = len(get_entries_from_db(
        #     "round_order",
        #     "rounds",
        #     "quiz_id = " + str(round_info['quiz_id']))
        # )

        # # Checks if the current Question is the first in the round
        # if int(round_info['round_order']) != 1:
        #     # Gets the question_id for the previous Question
        #     previous_round_info = get_entry_from_db(
        #         "round_id",
        #         "rounds",
        #         "round_order = " + str(int(round_info['round_order'])-1)
        #     )
        
        # # If it's the first Question
        # else:
        #     # Creates a blank dictionary
        #     previous_round_info = dict()

        # # Checks if the current Question is the last in the round
        # if int(round_info['round_order']) != number_of_rounds:
        #     # Gets the question_id for the next Question
        #     next_round_info = get_entry_from_db(
        #         "round_id",
        #         "rounds",
        #         "round_order = " + str(int(round_info['round_order'])+1)
        #     )
        # # If it's the last Question of the round
        # else:
        #     # Creates a blank dictionary
        #     next_round_info = dict()

    #    # Feeds data into HTML Jinja2 template
    #     return render_template(
    #         "quiz/make_a_quiz/rounds/round_template.html",
    #         name                = "Round Template",
    #         round_info          = round_info
    #         # question_info       = question_info,
    #         # number_of_rounds    = number_of_rounds,
    #         # next_round_info     = next_round_info,
    #         # previous_round_info = previous_round_info
    #     )
    
    # else:
    #     flash(request.form.get('round_id'))
    #     return redirect(url_for(
    #         'home'
    #     ))  



# This function will update the current Round's name, but only if the new name doesn't already exist for a Round in the associated quiz
@app.route('/update_round_name', methods=['GET', 'POST']) 
def update_round_name():
    # Check to see if the user is an admin       
    if admin_check and request.method == "POST":
        # If there's not already a Round with that name in the quiz, the round_name is updated
        update_db_entry(
            "rounds",
            "round_name = \"" + request.form.get('new_round_name') + "\"",
            "round_id = " + request.form.get('round_id')
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
            "round_description = \"" + request.form.get('new_round_description').replace("\"", "") + "\"",
            "round_id = " + str(request.form.get('round_id')) #Is str needed?
        )

        # The user is redirected to the Round template
        # Not needed in post if statement
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
            "question_id = " + str(request.form.get('question_id'))
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
            "question_id = \"" + request.form.get('question_id') + "\""
        )

        # Question Type information
        if question_info['question_type_id'] is not None:
            question_type = get_entry_from_db(
                "*",
                "question_type",
                "question_type_id = \"" + str(question_info['question_type_id']) + "\""
            )

            question_info.update(question_type)


            # This finds all the quizzes this round is not currentlu associated with
            question_types = compare_two_tables(
                "*",
                "question_type",
                "question_type_id",
                "questions",
                "question_id = \"" + request.form.get('question_id') + "\""
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
                "question_scoring_type_id = \"" + str(question_info['question_scoring_type_id']) + "\""
            )

            question_info.update(question_scoring_type)


            # This finds all the quizzes this round is not currentlu associated with
            question_scoring_types = compare_two_tables(
                "*",
                "question_scoring_type",
                "question_scoring_type_id",
                "questions",
                "question_id = \"" + request.form.get('question_id') + "\""
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
                "category_id = \"" + str(question_info['question_category_id']) + "\""
            )

            question_info.update(question_category)


            # This finds all the quizzes this round is not currentlu associated with
            question_categories = compare_two_tables_name(
                "*",
                "categories",
                "category_id",
                "question_category_id",
                "questions",
                "question_id = \"" + request.form.get('question_id') + "\""
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
            "question_id = \"" + request.form.get('question_id') + "\""
        )

        hints = sorted(hints, key=lambda k: k['hint_number']) 


        # Round information
        # Collects information on all the rounds this question is associated with
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.question_order",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.question_id = " + request.form.get('question_id')
        )

        # Loop through all the associated rounds to find their associated quizzes
        for associated_round in associated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_points, questions.question_difficulty, live.question_order, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = " + str(associated_round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        associated_round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        associated_round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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
                "live.quiz_id WHERE live.round_id = \"" + str(associated_round['round_id']) + "\""
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
            "question_id = \"" + request.form.get('question_id') + "\""
        )

        # Loop through all the associated rounds to find their associated quizzes
        for unassociated_round in unassociated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_points, questions.question_difficulty, live.question_order, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = " + str(unassociated_round['round_id'])
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        unassociated_round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        unassociated_round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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
                "live.quiz_id WHERE live.round_id = \"" + str(unassociated_round['round_id']) + "\""
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
            associated_round_info   = associated_round_info
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
        question_update         = request.form.get('question_update')
        question_update_field   = request.form.get('question_update_field')
        question_update         = question_update.replace("\"","")

        # Format the submitted data to work depending on what was updated
        if re.search("question_audio", question_update_field):
            question_update = re.sub("view", "preview", question_update)
        if re.search("question_video", question_update_field):
            question_update = re.sub("watch\?v\=", "embed/", question_update)
  
        # Puts quotation marks either side of the question update
        if question_update != "NULL":
            question_update = "\"" + question_update + "\""

        # Updates the question in the database    
        update_db_entry(
            "questions",
            question_update_field + " = " + question_update,
            "question_id = " + request.form.get('question_id')
        )

        # Redirects to the question template
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
                request.form.get("order_type")+"_order = 0",
                "quiz_id = \"" + request.form.get("quiz_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = " + request.form.get("old_order")
            )

            # This will shift all other orders up 1 from the "new order" to the "old order-1"
            for i in order:
                update_db_entry(
                    "live",
                    request.form.get("order_type")+"_order = " + str(i+1),
                    "quiz_id = \"" + request.form.get("quiz_id") + "\" AND " + request.form.get("order_type") + "_order = " + str(i)
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                request.form.get("order_type")+"_order = " + request.form.get("new_order"),
                "quiz_id = \"" + request.form.get("quiz_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = 0"
            )
    

        # If the new order is higher than the old order 
        else:
            # Create a list of numbers from the old order to the new order.
            order = list(range(int(request.form.get("old_order")),int(request.form.get("new_order"))+1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "live",
                request.form.get("order_type")+"_order = 0",
                "quiz_id = \"" + request.form.get("quiz_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = " + request.form.get("old_order")
            )

            # This will shift all other orders down 1 from the "new order +1" to the "old order"
            for i in range(len(order)):
                update_db_entry(
                    "live",
                    request.form.get("order_type")+"_order = " + str(order[i-1]),
                    "quiz_id = \"" + request.form.get("quiz_id") + "\" AND " + request.form.get("order_type")+"_order = " + str(order[i])
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                request.form.get("order_type")+"_order = " + request.form.get("new_order"),
                "quiz_id = \"" + request.form.get("quiz_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = 0"
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
                request.form.get("order_type")+"_order = 0",
                "question_id = \"" + request.form.get("question_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = " + request.form.get("old_order")
            )

            # This will shift all other orders up 1 from the "new order" to the "old order-1"
            for i in order:
                update_db_entry(
                    "live",
                    request.form.get("order_type")+"_order = " + str(i+1),
                    "round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type") + "_order = " + str(i)
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                request.form.get("order_type")+"_order = " + request.form.get("new_order"),
                "question_id = \"" + request.form.get("question_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = 0"
            )
    

        # If the new order is higher than the old order 
        else:
            # Create a list of numbers from the old order to the new order.
            order = list(range(int(request.form.get("old_order")),int(request.form.get("new_order"))+1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "live",
                request.form.get("order_type")+"_order = 0",
                "question_id = \"" + request.form.get("question_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = " + request.form.get("old_order")
            )

            # This will shift all other orders down 1 from the "new order +1" to the "old order"
            for i in range(len(order)):
                update_db_entry(
                    "live",
                    request.form.get("order_type")+"_order = " + str(order[i-1]),
                    "round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = " + str(order[i])
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "live",
                request.form.get("order_type")+"_order = " + request.form.get("new_order"),
                "question_id = \"" + request.form.get("question_id") + "\" AND round_id = \"" + request.form.get("round_id") + "\" AND " + request.form.get("order_type")+"_order = 0"
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
                "hint_id = \"" + request.form.get("hint_id") + "\""
            )

            # This will shift all other orders up 1 from the "new order" to the "old order-1"
            for i in order:
                update_db_entry(
                    "hints",
                    "hint_number = " + str(i+1),
                    "question_id = \"" + request.form.get("question_id") + "\" AND " + "hint_number = " + str(i)
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "hints",
                "hint_number = " + request.form.get("new_order"),
                "hint_id = \"" + request.form.get("hint_id") + "\""
            )
    

        # If the new order is higher than the old order 
        else:
            # Create a list of numbers from the old order to the new order.
            order = list(range(int(request.form.get("old_order")),int(request.form.get("new_order"))+1))
            # This is putting the current order to a placeholder value. No order should be 0, so is a safe placeholder value
            update_db_entry(
                "hints",
                "hint_number = 0",
                "hint_id = \"" + request.form.get("hint_id") + "\""
            )

            # This will shift all other orders down 1 from the "new order +1" to the "old order"
            for i in range(len(order)):
                update_db_entry(
                    "hints",
                    "hint_number = " + str(order[i-1]),
                    "question_id = \"" + request.form.get("question_id") + "\" AND " + "hint_number = " + str(order[i])
                )

            # This then changes the order from the placeholder order, to the new one
            update_db_entry(
                "hints",
                "hint_number = " + request.form.get("new_order"),
                "hint_id = \"" + request.form.get("hint_id") + "\""
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
            "live.quiz_id WHERE live.quiz_completed is NULL AND live.quiz_active is NULL"
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
            active_quiz_info      = active_quiz_info
        )

    else:
        return redirect(url_for(
            'home'
        )) 
    

# This function will use the quiz_id, round_id and question_id to display the host view for the current question
#This function will require work, now that a post form is the standard
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
            "live.quiz_id WHERE quizzes.quiz_id = " + str(request.form.get('quiz_id'))
        )

        # Collects information on all the rounds associated with the quiz
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.round_order, live.round_active, live.round_completed",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.quiz_id = " + request.form.get('quiz_id')
        )

        # Sorts the dictionaries of rounds in order of their round_order
        associated_round_info = sorted(associated_round_info, key=lambda k: k['round_order'])

        quiz_info['number_of_associated_rounds'] = len(associated_round_info)

        associated_questions = []
        for round in associated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_category_id, questions.question_difficulty, questions.question_points",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = " + str(round['round_id'])
            )
            for associated_question in associated_question_info:
                associated_questions.append(associated_question)
            
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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
                            "category_id = \"" + str(question_category) + "\""
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    quiz_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    quiz_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(question_category_id[0]) + "\""
                    )['category_name']
                else:
                    quiz_info['mode_question_category'] = "Not set"

        for round in associated_round_info:
            if round['round_active'] == 1:
                break
            if round['round_completed'] != 1 and quiz_info['quiz_active'] == 1:
                round['next_round'] = True
                break

        round_questions = common_values(
                "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points, live.question_order, live.question_active, live.question_completed, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_active = 1"
            )
        
        answers = common_values(
            "users.username, answers.answer_text, answers.hints_used, answers.answer_timestamp, answers.question_id, answers.round_id, answers.answer_correct",
            "answers",
            "users",
            "answers.user_id",
            "users.user_id WHERE answers.quiz_id = " + str(quiz_info['quiz_id'])
        )
        answers = sorted(answers, key=lambda k: k['answer_timestamp'])

        # Sorts the dictionaries of rounds in order of their round_order
        round_questions = sorted(round_questions, key=lambda k: k['question_order'])
        for question in round_questions:
            question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(question['question_category_id']) + "\""
                    )['category_name']
            
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

    
        active_question = common_value(
                "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points, questions.question_text, questions.question_type_id, questions.question_scoring_type_id, live.question_order, live.question_active, live.question_completed, live.round_id",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.question_active = 1"
            )

        if active_question:
            # Converts question_category_id and question_scoring_id to a their respective names
            active_question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(active_question['question_category_id']) + "\""
                    )['category_name']

            active_question['question_type'] = get_entry_from_db(
                        "question_type_name",
                        "question_type",
                        "question_type_id = \"" + str(active_question['question_type_id']) + "\""
                    )['question_type_name']
            
            active_question['question_scoring_type'] = get_entry_from_db(
                        "question_scoring_type_name",
                        "question_scoring_type",
                        "question_scoring_type_id = \"" + str(active_question['question_scoring_type_id']) + "\""
                    )['question_scoring_type_name']


        # Returns information for which users are ready to start the quiz
        participant_info = common_values(
            "users.username, participants.participant_ready",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE quiz_id = " + str(request.form.get('quiz_id')) #Is str needed?
        )

        if not count_not("participants", "participant_ready", "1")[0] > 0:
            quiz_info['quiz_ready'] = True

        if count("live", "round_completed", "1 AND quiz_id = " + str(request.form.get('quiz_id')))[0] == len(associated_round_info):
            quiz_info['quiz_end'] = True


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/host_a_quiz/host_live_quiz.html",
            name                    = quiz_info['quiz_name'],
            quiz_info               = quiz_info,
            associated_round_info   = associated_round_info,
            round_questions         = round_questions,
            active_question         = active_question,
            participant_info        = participant_info,
            answers                 = answers
        )
    
    else:
        flash("You can't just go straight to hosting the quiz")
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
                "quiz_id = " + str(request.form.get('quiz_id'))
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
            "round_id = " + str(request.form.get('round_id'))
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
        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "question_active = 1",
            "question_id = " + str(request.form.get('question_id'))
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
            "question_id = " + str(request.form.get('question_id'))
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

@app.route('/host_live_quiz/complete_round', methods=['GET', 'POST'])
def complete_round():
    if admin_check() and request.method == 'POST':
        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "round_active = NULL, round_completed = 1",
            "round_id = " + str(request.form.get('round_id'))
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

@app.route('/host_live_quiz/complete_quiz', methods=['GET', 'POST'])
def complete_quiz():
    if admin_check() and request.method == 'POST':
        # This update the value of active to TRUE in the database for the round  
        update_db_entry(
            "live",
            "quiz_active = NULL, quiz_completed = \"" + timestamp() + "\"",
            "quiz_id = " + str(request.form.get('quiz_id'))
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



# This function will update the database with whether the answer submitted by the user was correct or not
@app.route('/host_live_quiz/mark_answer', methods=['GET', 'POST'])
def mark_answer():
    # Check to see if the user is an admin
    if admin_check() and request.method == 'POST':
        # Updates the DB with whether the answer was correct or not
        update_db_entry(
            "answers",
            "answer_correct = " + request.form.get('marked_answer'),
            "user_id = " + str(request.form.get('user_id')) + " AND question_id = " + str(request.form.get('question_id'))
        )

        # Redirects the user back to the host live quiz
        return redirect(url_for(
            'host_live_quiz'
        ),
            code = 307
        )

    else:
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
        "participants.quiz_id INNER JOIN live on live.quiz_id = quizzes.quiz_id WHERE live.quiz_active = 1 AND participants.user_id = " + str(session['user_id'])
    )

    upcoming_quiz_info = common_values(
        "DISTINCT quizzes.quiz_id, quizzes.quiz_name, live.quiz_active",
        "quizzes",
        "participants",
        "quizzes.quiz_id",
        "participants.quiz_id INNER JOIN live on live.quiz_id = quizzes.quiz_id WHERE live.quiz_active IS NULL AND live.quiz_completed IS NULL AND participants.user_id = " + str(session['user_id'])
    )

    previous_quiz_info = common_values(
        "DISTINCT quizzes.quiz_id, quizzes.quiz_name",
        "quizzes",
        "participants",
        "quizzes.quiz_id",
        "participants.quiz_id INNER JOIN live on live.quiz_id = quizzes.quiz_id WHERE live.quiz_completed IS NOT NULL AND participants.user_id = " + str(session['user_id'])
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
            "live.quiz_id WHERE quizzes.quiz_id = " + str(request.form.get('quiz_id'))
        )

        # Collects information on all the rounds associated with the quiz
        associated_round_info = common_values(
            "rounds.round_id, rounds.round_name, rounds.round_description, live.round_order, live.round_active, live.round_completed",
            "rounds",
            "live",
            "rounds.round_id",
            "live.round_id WHERE live.quiz_id = " + request.form.get('quiz_id')
        )

        # Sorts the dictionaries of rounds in order of their round_order
        associated_round_info = sorted(associated_round_info, key=lambda k: k['round_order'])

        quiz_info['number_of_associated_rounds'] = len(associated_round_info)

        associated_questions = []
        for round in associated_round_info:
            # Collects information on all the quizzes this round is associated with
            associated_question_info = common_values(
                "questions.question_category_id, questions.question_difficulty, questions.question_points",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id WHERE live.round_id = " + str(round['round_id'])
            )
            for associated_question in associated_question_info:
                associated_questions.append(associated_question)
            
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
                                "category_id = \"" + str(question_category) + "\""
                            )['category_name']
                            mode_question_categories.append(question_category_name)
                        round['mode_question_category'] = " and ".join(mode_question_categories)
                    elif question_category_id is not None:
                        round['mode_question_category'] = get_entry_from_db(
                            "category_name",
                            "categories",
                            "category_id = \"" + str(question_category_id[0]) + "\""
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
                            "category_id = \"" + str(question_category) + "\""
                        )['category_name']
                        mode_question_categories.append(question_category_name)
                    quiz_info['mode_question_category'] = " and ".join(mode_question_categories)
                elif question_category_id is not None:
                    quiz_info['mode_question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(question_category_id[0]) + "\""
                    )['category_name']
                else:
                    quiz_info['mode_question_category'] = "Not set"

        for round in associated_round_info:
            if round['round_active'] == 1:
                break
            if round['round_completed'] != 1 and quiz_info['quiz_active'] == 1:
                round['next_round'] = True
                break

        round_questions = common_values(
                "questions.question_id, questions.question_tag, questions.question_scoring_type_id, questions.question_type_id, questions.question_category_id, questions.question_difficulty, questions.question_points, questions.question_text, live.question_order, live.question_active, live.question_completed, answers.answer_text, answers.hints_used",
                "questions",
                "live",
                "questions.question_id",
                "live.question_id LEFT OUTER JOIN answers on answers.question_id = questions.question_id WHERE live.round_active = 1"
            )

        # Sorts the dictionaries of rounds in order of their round_order
        round_questions = sorted(round_questions, key=lambda k: k['question_order'])
        for question in round_questions:
            question['question_category'] = get_entry_from_db(
                        "category_name",
                        "categories",
                        "category_id = \"" + str(question['question_category_id']) + "\""
                    )['category_name']
            
            question['question_type'] = get_entry_from_db(
                "question_type_name",
                "question_type",
                "question_type_id = \"" + str(question['question_type_id']) + "\""
            )['question_type_name']
            
            question['question_scoring_type'] = get_entry_from_db(
                        "question_scoring_type_name",
                        "question_scoring_type",
                        "question_scoring_type_id = \"" + str(question['question_scoring_type_id']) + "\""
                    )['question_scoring_type_name']
            
        for question in round_questions:
            if question['question_active'] == 1:
                break
            if question['question_completed'] != 1:
                question['next_question'] = True
                break

        for question in reversed(round_questions):
            if "next_question" in question or question['question_active']:
                break  # Stop searching if found
            elif quiz_info['quiz_active'] == True:  # Executed only if the loop completes without finding the key
                quiz_info['round_end'] = True

    
        # active_question = common_value(
        #         "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points, questions.question_text, questions.question_type_id, questions.question_scoring_type_id, live.question_order, live.question_active, live.question_completed",
        #         "questions",
        #         "live",
        #         "questions.question_id",
        #         "live.question_id WHERE live.question_active = 1"
        # )
        
        active_question = common_value(
            "questions.question_id, questions.question_tag, questions.question_category_id, questions.question_difficulty, questions.question_points, questions.question_text, questions.question_type_id, questions.question_scoring_type_id, live.round_id, live.question_order, live.question_active, live.question_completed, answers.answer_text, answers.hints_used",
            "questions",
            "live",
            "questions.question_id",
            "live.question_id LEFT OUTER JOIN answers on answers.question_id = questions.question_id WHERE live.question_active = 1"
        )

        if active_question:
            # Converts question_category_id and question_scoring_id to a their respective names
            active_question['question_category'] = get_entry_from_db(
                "category_name",
                "categories",
                "category_id = \"" + str(active_question['question_category_id']) + "\""
            )['category_name']

            active_question['question_type'] = get_entry_from_db(
                "question_type_name",
                "question_type",
                "question_type_id = \"" + str(active_question['question_type_id']) + "\""
            )['question_type_name']
            
            active_question['question_scoring_type'] = get_entry_from_db(
                        "question_scoring_type_name",
                        "question_scoring_type",
                        "question_scoring_type_id = \"" + str(active_question['question_scoring_type_id']) + "\""
                    )['question_scoring_type_name']


        # Returns information for which users are ready to start the quiz
        all_participant_info = common_values(
            "users.username, users.user_id, participants.participant_ready",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE quiz_id = " + str(request.form.get('quiz_id')) #Is str needed?
        )

        participant_info = common_value(
            "users.username, participants.participant_ready",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE participants.quiz_id = " + str(request.form.get('quiz_id')) + " AND participants.user_id = " +  str(session['user_id'])#Is str needed?
        )

        if not count_not("participants", "participant_ready", "1")[0] > 0:
            quiz_info['quiz_ready'] = True

        if not count_not("live", "round_completed", "1 AND quiz_id = " + str(request.form.get('quiz_id')))[0] > 0:
            if quiz_info['quiz_completed']:
                quiz_info['quiz_end'] = True


        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/join_a_quiz/live_quiz.html",
            name                    = quiz_info['quiz_name'],
            quiz_info               = quiz_info,
            associated_round_info   = associated_round_info,
            round_questions         = round_questions,
            active_question         = active_question,
            participant_info        = participant_info,
            all_participant_info    = all_participant_info
        )
    
    else:
        flash("You can't just go straight to hosting the quiz")
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
            "user_id = " + str(request.form.get('user_id')) + " AND quiz_id = " + request.form.get('quiz_id')
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
                "user_id = " + str(request.form.get('user_id')) + " AND quiz_id = " + request.form.get('quiz_id')
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
        # This checks if the user has already submitted an answer before
        if check_single_db(
            "user_id",
            "answers",
            "user_id = \"" + str(session['user_id']) + "\" AND question_id = \"" + str(request.form.get("question_id")) + "\" AND round_id = \"" + str(request.form.get("round_id")) + "\" AND quiz_id = \"" + str(request.form.get("quiz_id")) + "\""
        ):
            # This updates the Answers table with the new answer
            update_db_entry(
                "answers",
                "answer_text = \"" + request.form.get("new_answer").replace("\"", "") + "\", answer_correct = NULL, answer_timestamp = \"" + timestamp() + "\"",
                "user_id = " + str(session['user_id']) + " AND question_id = " + str(request.form.get("question_id")) + " AND round_id = " + str(request.form.get("round_id")) + " AND quiz_id = " + str(request.form.get("quiz_id"))
            )

        # If this is the first answer being submitted
        else:
            # Insert the new answer into the table
            insert_db_entry(
                "answers",
                "user_id, question_id, round_id, quiz_id, answer_text, answer_timestamp",
                "\"" + str(session['user_id']) + "\", \"" + str(request.form.get("question_id")) + "\", \"" + str(request.form.get("round_id")) + "\", \"" + str(request.form.get("quiz_id")) + "\", \"" + request.form.get("new_answer").replace("\"", "") + "\", \"" + timestamp() + "\""
            )

        # Redirects user to the Live quiz page
        flash("Answer updated")
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
                "live.quiz_id INNER JOIN participants ON quizzes.quiz_id = participants.quiz_id WHERE live.quiz_completed is not NULL AND live.quiz_active is NULL AND participants.user_id = " + str(session['user_id'])
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
            "participants.participant_position, users.username, participants.participant_score",
            "users",
            "participants",
            "users.user_id",
            "participants.user_id WHERE quiz_id = " + str(request.form.get('quiz_id')) #Is str needed?
        )

        # Gets the name of the quiz
        quiz_info = get_entry_from_db(
                "quiz_name",
                "quizzes",
                "quiz_id = " + str(request.form.get('quiz_id'))
            )

        def sort_by_score(dict_item):
            return dict_item["participant_score"]

        participant_info = sorted(participant_info, key=sort_by_score)

        # Feeds data into HTML Jinja2 template
        return render_template(
            "quiz/results/results.html",
            name                = quiz_info['quiz_name'] + " Results",
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
        "misc/t&c.html",
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