-- Turns User 1 into an admin
USE quiz;
UPDATE users SET user_admin = 1 WHERE user_id = 1;