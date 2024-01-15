USE quiz;

-- Categories Table
INSERT IGNORE INTO categories
(category_name, category_description) VALUES
("General Knowledge", "This category covers a wide range of topics about the world, including science, technology, current events, geography, history, culture, and more. It's all about testing your broad understanding of the world around you."),
("History", "Travel back in time with this category! Test your knowledge of major historical events, figures, empires, wars, and social movements. Questions may span across different periods and regions of the world."),
("2023","This category focuses on specific events, news, trends, and popular culture from these years. Expect questions about major headlines, technological advancements, political happenings, and cultural phenomena that occurred in these timeframes."),
("Politics","This category delves into the world of government, elections, policies, and current political events. Be prepared for questions about leaders, ideologies, systems of government, and political debates."),
("Music","Covers diverse musical genres, artists, albums, instruments, musical theory, and significant moments in music history."),
("Board Games","Challenges your knowledge of classic and modern board games, gameplay mechanics, strategies, trivia, and popular titles."),
("Geography","Get your atlas ready! This category will test your knowledge of maps, countries, continents, oceans, capitals, landmarks, and geographical features. Be prepared for questions about physical and political geography."),
("Culture and Religion","This category explores the diverse cultures and religious traditions of the world. Expect questions about customs, beliefs, practices, holidays, art, music, and folklore from different cultures and religions."),
("Entertainment","Get ready for some fun! This category covers a wide range of entertainment topics, including music, movies, TV shows, books, celebrities, pop culture, and trends."),
("Video Games","Level up your knowledge in this category! Test your skills with questions about popular video games, consoles, characters, storylines, genres, and gaming history."),
("TV and Movie","Lights, camera, action! This category puts your knowledge of cinema and television to the test. Be prepared for questions about movies, TV shows, actors, directors, genres, awards, and iconic scenes."),
("Literature","Unleash your inner bookworm! This category explores the world of literature, including classic novels, authors, poetry, genres, literary themes, and famous quotes."),
("Theatre, Musicals and Plays","Take a bow! This category is all about the dramatic arts. Test your knowledge of plays, musicals, theatre history, playwrights, actors, and famous stage productions."),
("2024","This category focuses on specific events, news, trends, and popular culture from these years. Expect questions about major headlines, technological advancements, political happenings, and cultural phenomena that occurred in these timeframes."),
("Me","This category is a bit of a mystery! It might involve questions about your personal preferences, experiences, or even hidden talents. Come prepared to reveal something new about yourself!");


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
("Red Shell", "If you throw it forwards/behind, you have a 100%/50% chance of taking 5 points off the person infront/behind.", "90", "100", "50", NULL, "-5"),
("Lightning", "Take 3 points from all people ahead of you", "50", "100", NULL, NULL, "-3"),
("Blue Shell", "Guaranteed  to hit 1st place and all those around them. You won't be affected.", "10", "100", NULL, NULL, "-10"),
("1up Mushroom", "Move up a position in the Quiz.", "20", NULL, NULL, "100", NULL),
("Coin", "Gain a point", "100", NULL, NULL, "100", "1"),
("Red Mushroom", "Gain 3 points", "50", NULL, NULL, "100", "3"),
("Golden Mushroom", "Gain 5 points", "30", NULL, NULL, "100", "5"),
("Golden Pipe", "Move to 1st place! Lucky bastard!", "5", NULL, NULL, "100", NULL);