# This is on a clean RHEL9 EC2 instance
sudo yum update -y
# install git
sudo yum install git -y
# pull down the app
git clone https://github.com/TDCole21/tom_quiz_app.git
# install python
sudo yum install python -y
# manually create the info.py file
# install pip
sudo yum install pip -y
# install flask
pip install Flask
pip install flask_mysqldb