USE quiz;
SELECT username, user_id FROM users;
UPDATE participants
SET participant_item_id = 5 WHERE user_id = 2;