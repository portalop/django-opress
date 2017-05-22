#!/bin/sh
cd /home/projects/hispaniae
git add *
git commit -a -m "Subida de código y virtualenv a producción"
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete --exclude 'media' /home/projects/hispaniae/ root@dominicos-web1.dominicos.org:/home/projects/hispaniae
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete --exclude "lib/python2.7/site-packages/_mysql.so" /home/.virtualenvs/hispaniae/ root@dominicos-web1.dominicos.org:/home/.virtualenvs/hispaniae

ssh root@dominicos-web1.dominicos.org 'export WORKON_HOME=/home/.virtualenvs; source /usr/local/bin/virtualenvwrapper.sh; workon hispaniae; python /home/projects/hispaniae/manage.py clear_cache'
