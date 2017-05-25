#!/bin/bash
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# -----------------------------------------
# |           Project settings            |
# -----------------------------------------

echo "Reading config..." >&2
source create_project.cfg

PRODUCTION_DB_PASSWORD=$(python -c "import random,string;print ''.join([random.SystemRandom().choice(\"{}{}{}{}\".format(string.ascii_letters, string.ascii_letters, string.ascii_letters, string.digits)) for i in range(63)])")
DEBUG_DB_PASSWORD=$(python -c "import random,string;print ''.join([random.SystemRandom().choice(\"{}{}{}{}\".format(string.ascii_letters, string.ascii_letters, string.ascii_letters, string.digits)) for i in range(63)])")
USER_PASSWORD=$(python -c "import random,string;print ''.join([random.SystemRandom().choice(\"{}{}{}{}\".format(string.ascii_letters, string.ascii_letters, string.ascii_letters, string.digits)) for i in range(63)])")
ADMIN_PASSWORD=$(python -c "import random,string;print ''.join([random.SystemRandom().choice(\"{}{}{}{}\".format(string.ascii_letters, string.ascii_letters, string.ascii_letters, string.digits)) for i in range(63)])")

# -----------------------------------------

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
if [ ! -d "$PROJECT_NAME" ]; then
	export WORKON_HOME=/home/.virtualenvs
	source /usr/local/bin/virtualenvwrapper.sh
	# mkvirtualenv $PROJECT_NAME
	workon $PROJECT_NAME

	echo "installing required packages on virtualenv"
	# pip install django
	# cd $DIR/apps/django-contrib-comments
	# python $DIR/apps/django-contrib-comments/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-contrib-comments/dist/django-contrib-comments-1.7.0.dev1.tar.gz
	# cd $DIR/apps/django-fluent-comments
	# python $DIR/apps/django-fluent-comments/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-fluent-comments/dist/django-fluent-comments-1.2.tar.gz
	# cd $DIR/apps/django-taggit
	# python $DIR/apps/django-taggit/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-taggit/dist/django-taggit-0.18.0.tar.gz
	# cd $DIR/apps/django-taggit-labels
	# python $DIR/apps/django-taggit-labels/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-taggit-labels/dist/django-taggit-labels-0.4.1.tar.gz
	# cd $DIR/apps/django-grappelli
	# #compass compile $DIR/apps/django-grappelli/grappelli/compass
	# python $DIR/apps/django-grappelli/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-grappelli/dist/django-grappelli-2.9.1.tar.gz
	# cd $DIR/apps/django-photologue
	# python $DIR/apps/django-photologue/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-photologue/dist/django-photologue-3.1.dev0.tar.gz
	# cd $DIR/apps/django-filebrowser
	# python $DIR/apps/django-filebrowser/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-filebrowser/dist/django-filebrowser-3.7.2.tar.gz
	# cd $DIR/apps/django-mptt
	# python $DIR/apps/django-mptt/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-mptt/dist/django-mptt-0.8.7.tar.gz
	# cd $DIR/apps/django-mptt-admin
	# python $DIR/apps/django-mptt-admin/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-mptt-admin/dist/django-mptt-admin-0.3.1.tar.gz
	# cd $DIR/apps/django-tinymce
	# python $DIR/apps/django-tinymce/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-tinymce/dist/django-tinymce-2.7.0.dev0.tar.gz
	# cd $DIR/apps/django-opress
	# python $DIR/apps/django-opress/setup.py sdist
	# pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-opress/dist/opress-0.1.tar.gz
	# pip install django-sortedm2m
	# pip install djangorestframework
	# pip install django-statsd
	# pip install django-debug-toolbar
	# pip install MySQL-python
	# pip install ExifRead
	# pip install Pillow
	# pip install django-subdomains
	# pip install requests
	# pip install django-taggit-serializer
	# pip install beautifulsoup4
	# pip install django-ipware
	# pip install python-memcached
	echo "Creating project $PROJECT_NAME on folder $DIR"

	function reemplazar {
  		sed -i "s/$(echo $1 | sed -e 's/\([[\/.*]\|\]\)/\\&/g')/$(echo $2 | sed -e 's/[\/&]/\\&/g')/g" $3
	}
	cd $DIR
	django-admin startproject $PROJECT_NAME
	cp -r $PROJECT_TEMPLATE/. $PROJECT_NAME
	cp $PROJECT_NAME/sample_project/*.* $PROJECT_NAME/$PROJECT_NAME/
	rm -r $PROJECT_NAME/sample_project
	find $DIR/$PROJECT_NAME/templates -type f -exec sed -i "s/\[:SAMPLE_PROJECT:\]/$PROJECT_NAME/g" {} \;
	mv $DIR/$PROJECT_NAME/static/sample_project $DIR/$PROJECT_NAME/static/$PROJECT_NAME
	cdsitepackages
	mv $DIR/$PROJECT_NAME/NginxMemCacheMiddleWare.py .
	cd $DIR

	echo "Setting up Django, uWSGI and Nginx config files"
	SECRET_KEY=$(python -c "import random,string;print ''.join([random.SystemRandom().choice(\"{}{}{}\".format(string.ascii_letters, string.digits, string.punctuation.replace('\'', '').replace('\\\\', ''))) for i in range(63)])")
	cd $PROJECT_NAME
	reemplazar "[:SECRET_KEY:]" "$SECRET_KEY" $PROJECT_NAME/settings.py
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" $PROJECT_NAME/settings.py
	reemplazar "[:PRODUCTION_ALLOWED_HOSTS:]" "$PRODUCTION_ALLOWED_HOSTS" $PROJECT_NAME/settings.py
	reemplazar "[:DEBUG_ALLOWED_HOSTS:]" "$DEBUG_ALLOWED_HOSTS" $PROJECT_NAME/settings.py
	reemplazar "[:PRODUCTION_DB_PASSWORD:]" "$PRODUCTION_DB_PASSWORD" $PROJECT_NAME/settings.py
	reemplazar "[:DEBUG_DB_PASSWORD:]" "$DEBUG_DB_PASSWORD" $PROJECT_NAME/settings.py
	reemplazar "[:PROJECT_DIR:]" "$DIR/$PROJECT_NAME" $PROJECT_NAME/settings.py
	reemplazar "[:PROJECT_TITLE:]" "$PROJECT_TITLE" $PROJECT_NAME/settings.py
	reemplazar "[:OPRESS_CONTACT_EMAIL:]" "$OPRESS_CONTACT_EMAIL" $PROJECT_NAME/settings.py
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" $PROJECT_NAME/urls.py
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" $PROJECT_NAME/wsgi.py
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" deploy.sh
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" deploy_code.sh
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" install-apps.sh
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" sample_project_uwsgi.ini
	reemplazar "[:PROJECT_DIR:]" "$DIR/$PROJECT_NAME" sample_project_uwsgi.ini
	reemplazar "[:SAMPLE_PROJECT:]" "$PROJECT_NAME" sample_project_nginx.conf
	reemplazar "[:PROJECT_DIR:]" "$DIR/$PROJECT_NAME" sample_project_nginx.conf
	reemplazar "[:MAIN_DOMAIN:]" "$MAIN_DOMAIN" sample_project_nginx.conf
	reemplazar "[:MY_IP:]" "$MY_IP" sample_project_nginx.conf
	UWSGI_PORT=$(grep 127.0 /etc/uwsgi/vassals/*.* | grep -o '....$' | sort -r | head -1)
	reemplazar "[:UWSGI_PORT:]" "$UWSGI_PORT" sample_project_uwsgi.ini
	python manage.py collectstatic --noinput
	mv sample_project_nginx.conf /etc/nginx/sites-available/$PROJECT_NAME.conf
	mv sample_project_uwsgi.ini /etc/uwsgi/vassals/$PROJECT_NAME.ini
	ln -s /etc/nginx/sites-available/$PROJECT_NAME.conf /etc/nginx/sites-enabled/

	echo "Setting up linux user permissions"
	groupadd $PROJECT_NAME
	useradd -g$PROJECT_NAME -s /usr/sbin/nologin $PROJECT_NAME
	#echo "$PROJECT_NAME:$USER_PASSWORD" | chpasswd
	chown -R root:root $DIR/$PROJECT_NAME
	chown $PROJECT_NAME:$PROJECT_NAME $DIR/$PROJECT_NAME
	chmod -R 644 $DIR/$PROJECT_NAME
	find $DIR/$PROJECT_NAME -type f -exec chmod 644 {} \;
	find $DIR/$PROJECT_NAME -type d -exec chmod 755 {} \;
	chmod 744 $DIR/$PROJECT_NAME/manage.py

	echo "Restarting web server..."
	rm $DIR/$PROJECT_NAME/$PROJECT_NAME.log
	$DIR/restart_uwsgi.sh

	echo "Creating and migrating MySql database"
	mysql -u root -p$ROOT_DB_PASSWORD <<EOF
DROP USER $PROJECT_NAME@localhost;
DROP DATABASE $PROJECT_NAME;
CREATE DATABASE $PROJECT_NAME /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci */;
CREATE USER $PROJECT_NAME@localhost IDENTIFIED BY '$DEBUG_DB_PASSWORD';
GRANT ALL PRIVILEGES ON $PROJECT_NAME.* TO $PROJECT_NAME@localhost;
FLUSH PRIVILEGES;
EOF
	$DIR/$PROJECT_NAME/manage.py makemigrations opress
	$DIR/$PROJECT_NAME/manage.py migrate

	echo "Creating superuser with name 'admin' and password '$ADMIN_PASSWORD'"
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | $DIR/$PROJECT_NAME/manage.py shell
else
	echo "La carpeta de proyecto $PROJECT_NAME ya existe"
fi
