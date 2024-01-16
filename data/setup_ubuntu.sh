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