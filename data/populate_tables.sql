USE quiz;

-- Categories Table
INSERT IGNORE INTO categories
(category_name, category_description) VALUES
("General Knowledge", "Information about stuff"),
("History", "Shit that already happened"),
("2023",""),
("Politics",""),
("Music",""),
("Geography",""),
("Culture and Religion",""),
("Entertainment",""),
("Video Games",""),
("TV and Movie",""),
("Literature",""),
("Theatre, Musicals and Plays",""),
("2024",""),
("Me","");


-- Question Scoring Type Table
INSERT IGNORE INTO question_scoring_type
(question_scoring_type_name, question_scoring_type_description) VALUES
("Fastest Finger", "The fastest marked correct answer earns the full point value of the question. Each subsequent marked correct answer receives one point less."),
("Right and Wrong", "Earn the full point value of this question if you are marked correct, nothing if you are marked wrong.");

-- Question Type Table
INSERT IGNORE INTO question_type
(question_type_name, question_type_description) VALUES
("Text", "Users submit text answers"),
("Multiple Choice", "The Users will be presented multiple choice answers. This hasn't been coded yet");

-- Items Table
INSERT IGNORE INTO items
(item_name, item_description, item_rarity, chance_forwards, chance_backwards, chance_use, item_points) VALUES
("Banana", "If you throw it forwards/behind, you have a 50%/75% chance of taking 5 points off the person infront/behind.", "100", "50", "75", NULL, "-5"),
("Green Shell", "If you throw it forwards/behind, you have a 75%/50% chance of taking 5 points off the person infront/behind.", "100", "75", "50", NULL, "-5"),
("Red Shell", "If you throw it forwards/behind, you have a 100%/50% chance of taking 5 points off the person infront/beghind.", "90", "100", "50", NULL, "-5"),
("Lightning", "Take 3 points from all people ahead of you", "50", "100", NULL, NULL, "-3"),
("Blue Shell", "Take 10 points from 1st, 5 from 2nd, 2 from 3rd and 1 from 4th. If you are in the top 4, you won't loose points", "10", "100", NULL, NULL, "-10"),
("1up Mushroom", "Move up a position in the Quiz.", "20", NULL, NULL, "100", NULL),
("Coin", "Gain a point", "100", NULL, NULL, "100", "1"),
("Red Mushroom", "Gain 3 points", "50", NULL, NULL, "100", "3"),
("Golden Mushroom", "Gain 5 points", "30", NULL, NULL, "100", "5"),
("Golden Pipe", "Move to 1st place! Lucky bastard!", "5", NULL, NULL, "100", NULL);