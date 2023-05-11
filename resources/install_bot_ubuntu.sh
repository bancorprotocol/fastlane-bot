# clone the config repo
git clone https://github.com/oditorium/config

# 010_init_upgrade
apt -y update
apt -y upgrade
apt -y autoremove

# 020_init_essentials
apt -y install git
apt -y install supervisor
apt -y install build-essential
apt -y install bc
apt -y install mosh
apt -y install screenfetch
apt -y install tree

# https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart
# apt -y install postgresql postgresql-contrib
# systemctl restart postgresql.service
# systemctl enable postgresql.service
# sudo -i -u postgres
# psql
# ALTER USER postgres WITH PASSWORD 'postgres';
# ALTER USER postgres WITH PASSWORD 'b2742bade1f3a271c55eef069e2f19903aa0740c';
# quit
# exit


# 030_init_jupyter

apt -y install python3 python3-pip
apt -y install python-is-python3
apt -y install python3-dev

pip3 install --upgrade pip
pip3 install jupyterlab
pip3 install jupytext
pip3 install pyqrcode

#jupyter notebook --allow-root
#jupyter notebook --port=9999 --allow-root

pip3 install pytest
pip3 install setuptools
pip3 install requests
pip3 install python-dotenv
pip3 install click
pip3 install dataclass_wizard

pip3 install pandas
pip3 install numpy
pip3 install scipy
pip3 install matplotlib
pip3 install tabulate
pip3 install cvxpy
pip3 install networkx

pip3 install sqlalchemy
pip3 install sqlalchemy_utils
pip3 install alchemy-sdk
pip3 install psycopg2-binary
#pip3 install psycopg2
#pip3 install pyarrow
#pip3 install fastparquet

pip3 install eth-brownie
pip3 install web3
pip3 install hexbytes

pip3 install joblib
pip3 install psutil

## IMAGE -- ABOT4-STAGE1

cd ~
cd config/components
cp ../_etc/home/profile ~/.profile
cp ../_etc/home/gitconfig ~/.gitconfig
cp ../_etc/home/gitignore_global ~/.gitignore_global
cp ../_etc/home/locations ~/.locations
cp ../_etc/home/bash_aliases ~/.bash_aliases

mkdir fastlanebot
cd fastlanebot
git init

# git remote add a4 root@64.227.114.80:/root/fastlanebot
# git co main
# git co -b a4
# git push a4 a4

git checkout a4
git reset --hard a4

cd ~
cd fastlanebot
echo export WEB3_ALCHEMY_PROJECT_ID="MOO" >> .env
echo export ETH_PRIVATE_KEY_BE_CAREFUL="0xMOO" >> .env
echo export ETH_PRIVATE_KEY_NAME="MOO" >> .env
echo export POSTGRES_PASSWORD="MOO" >> .env
echo export POSTGRES_USER="tsdbadmin" >> .env
echo export POSTGRES_PORT="27140" >> .env
echo export POSTGRES_DB="defaultdb" >> .env
echo export POSTGRES_HOST="arbbot-stefan-bancor-659d.a.timescaledb.io"  >> .env
vi .env


cd ~
cd fastlanebot
brownie networks update_provider alchemy https://eth-{}.alchemyapi.io/v2/$WEB3_ALCHEMY_PROJECT_ID
brownie networks modify mainnet provider=alchemy`
brownie networks set_provider alchemy
brownie networks list

# from here better run manually

echo <<'EOF' >> /etc/supervisor/conf.d/carbon_fastlane.conf
;*******************************************************************
; carbon_fastlane
;*******************************************************************
[program:carbon_fastlane]
command=/root/fastlanebot/run_supervisor_ubuntu
autostart=true
autorestart=true
startsecs=10
startretries=3
killasgroup=true
stopasgroup=true
redirect_stderr=false
stdout_logfile=/var/log/carbon_fastlane_output.log
stderr_logfile=/var/log/carbon_fastlane_error.log
EOF

cat /etc/supervisor/conf.d/carbon_fastlane.conf
#vi /etc/supervisor/conf.d/carbon_fastlane.conf
supervisorctl reload
supervisorctl status
supervisorctl restart carbon_fastlane

cd ~
cd fastlanebot
ln -s /var/log/carbon_fastlane_output.log output.log
ln -s /var/log/carbon_fastlane_error.log error.log
tail -f error.log

## IMAGE -- ABOT4-STAGE2

