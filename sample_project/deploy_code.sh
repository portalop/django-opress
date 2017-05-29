#!/bin/sh
cd /home/projects/[:SAMPLE_PROJECT:]
#git add *
#git commit -a -m "Subida de código y virtualenv a producción"
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete --exclude 'media' /home/projects/[:SAMPLE_PROJECT:]/ root@dominicos-web1.dominicos.org:/home/projects/[:SAMPLE_PROJECT:]
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress --delete --exclude "lib/python2.7/site-packages/_mysql.so" /home/.virtualenvs/[:SAMPLE_PROJECT:]/ root@dominicos-web1.dominicos.org:/home/.virtualenvs/[:SAMPLE_PROJECT:]

ssh root@dominicos-web1.dominicos.org 'export WORKON_HOME=/home/.virtualenvs; source /usr/local/bin/virtualenvwrapper.sh; workon [:SAMPLE_PROJECT:]; python /home/projects/[:SAMPLE_PROJECT:]/manage.py clear_cache'
