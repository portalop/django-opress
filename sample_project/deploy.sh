#!/bin/sh

cd /home/projects/[:SAMPLE_PROJECT:]
#git add *
#git commit -a -m "Subida de templates y static files a producción"
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete /home/projects/[:SAMPLE_PROJECT:]/static/ root@dominicos-web1.dominicos.org:/home/projects/[:SAMPLE_PROJECT:]/static
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete /home/projects/[:SAMPLE_PROJECT:]/templates/ root@dominicos-web1.dominicos.org:/home/projects/[:SAMPLE_PROJECT:]/templates

ssh root@dominicos-web1.dominicos.org 'export WORKON_HOME=/home/.virtualenvs; source /usr/local/bin/virtualenvwrapper.sh; workon [:SAMPLE_PROJECT:]; python /home/projects/[:SAMPLE_PROJECT:]/manage.py clear_cache'
