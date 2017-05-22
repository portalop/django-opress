#!/bin/sh

cd /home/projects/hispaniae
git add *
git commit -a -m "Subida de templates y static files a producción"
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete /home/projects/hispaniae/static/ root@dominicos-web1.dominicos.org:/home/projects/hispaniae/static
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete /home/projects/hispaniae/templates/ root@dominicos-web1.dominicos.org:/home/projects/hispaniae/templates

ssh root@dominicos-web1.dominicos.org 'export WORKON_HOME=/home/.virtualenvs; source /usr/local/bin/virtualenvwrapper.sh; workon hispaniae; python /home/projects/hispaniae/manage.py clear_cache'
