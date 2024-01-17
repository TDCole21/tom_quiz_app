# This is on a clean Ubunutu EC2 instance
sudo apt update -y
# install git
sudo apt install git -y
# pull down the app
git clone https://github.com/TDCole21/tom_quiz_app.git
# install python
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config -y
# manually create the info.py file
# install pip
sudo apt install pip -y
pip install mysqlclient
# install flask
pip install Flask
pip install flask_mysqldb
pip install multidict
# install nginx
sudo apt install nginx -y
# Create a new conf for port 5000
sudo vim /etc/nginx/conf.d/quiz.conf
# server {

#     listen      80;
#     server_name functions;

#     location / {

#         proxy_pass http://localhost:5000;

#     }

# }
# server_name is what appears when you run app.py

# Connect to RDS
sudo apt-get install mariadb-client -y
mysql -h <rds-url> -P 3306 -u admin -p

# Turn app into a service
sudo vim /etc/systemd/system/flask.service
# [Unit]
# Description=My Quiz App
# [Service]
# User=ubuntu

# ExecStart=/home/ubuntu/tom_quiz_app/installation.sh

# [Install]
# WantedBy=multi-user.target

chmod +x /home/ubuntu/tom_quiz_app/ -R
sudo systemctl daemon-reload
sudo systemctl start flask