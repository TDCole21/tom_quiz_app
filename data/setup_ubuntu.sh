# This is on a clean RHEL9 EC2 instance
sudo apt update -y
# install git
sudo apt install git -y
# pull down the app
git clone https://github.com/TDCole21/tom_quiz_app.git
# install python
sudo apt install python -y
# manually create the info.py file
# install pip
sudo apt install pip -y
# install flask
pip install Flask
pip install flask_mysqldb