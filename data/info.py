# Database setup

# From Windows
# I created an EC2 instance running Linux, and saved the PEM file in this directory
# Make sure the EC2 instance is running, then in VSCode terminal, run:
# ssh -i "quiz-rds.pem" ubuntu@ec2-34-245-51-155.eu-west-1.compute.amazonaws.com
# Note, when you stop and start the instance, it'll have a different IP address, so this code will need to be altered.
# Then on the EC2 Linux instance, run the below linux command

# From Linux
# mysql -h quiz.cbpf0qmeaxbr.eu-west-1.rds.amazonaws.com -P 3306 -u admin -p
# PaB98CeB65OaK91

# On Local Machine
# I installed mysql 8 on the machine and start the service
# Then using credentials in info.py I connect to the database 

# Cloud
# mysql_host = "quiz.cbpf0qmeaxbr.eu-west-1.rds.amazonaws.com"
# mysql_user = "admin"
# mysql_password = "PaB98CeB65OaK91"
# mysql_db = "Quiz"

# Local Host
mysql_host = "localhost"
mysql_user = "root"
mysql_password = "MidnaIsTheBest22"
mysql_db = "quiz"

# Local Host2
# mysql_host = "127.0.0.1"
# mysql_user = "root"
# mysql_password = "PaB98CeB65OaK91"
# mysql_db = "quiz"
