#!/bin/bash
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export WORKON_HOME=/home/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
workon hispaniae

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
echo $DIR
while [ "$1" != "" ]; do
    echo "Reinstalando la app $1"

        if [ "$1" = "opress" ]; then
            cd $DIR/apps/django-opress
            python $DIR/apps/django-opress/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-opress/dist/opress-0.1.tar.gz
        fi
        if [ "$1" = "comments" ]; then
            cd $DIR/apps/django-contrib-comments
            python $DIR/apps/django-contrib-comments/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-contrib-comments/dist/django-contrib-comments-1.7.0.dev1.tar.gz
            cd $DIR/apps/django-fluent-comments
            python $DIR/apps/django-fluent-comments/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-fluent-comments/dist/django-fluent-comments-1.2.tar.gz
        fi
        if [ "$1" = "taggit" ]; then
            cd $DIR/apps/django-taggit
            python $DIR/apps/django-taggit/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-taggit/dist/django-taggit-0.18.0.tar.gz
        fi
        if [ "$1" = "taggit-labels" ]; then
            cd $DIR/apps/django-taggit-labels
            python $DIR/apps/django-taggit-labels/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-taggit-labels/dist/django-taggit-labels-0.4.1.tar.gz
        fi
        if [ "$1" = "grappelli" ]; then
            cd $DIR/apps/django-grappelli
            #compass compile $DIR/apps/django-grappelli/grappelli/compass
            python $DIR/apps/django-grappelli/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-grappelli/dist/django-grappelli-2.9.1.tar.gz
        fi
        if [ "$1" = "photologue" ]; then
            cd $DIR/apps/django-photologue
            python $DIR/apps/django-photologue/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-photologue/dist/django-photologue-3.1.dev0.tar.gz
        fi
        if [ "$1" = "filebrowser" ]; then
            cd $DIR/apps/django-filebrowser
            python $DIR/apps/django-filebrowser/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-filebrowser/dist/django-filebrowser-3.7.2.tar.gz
        fi
        if [ "$1" = "mptt" ]; then
            cd $DIR/apps/django-mptt
            python $DIR/apps/django-mptt/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-mptt/dist/django-mptt-0.7a0.tar.gz
        fi
        if [ "$1" = "mptt-admin" ]; then
            cd $DIR/apps/django-mptt-admin
            python $DIR/apps/django-mptt-admin/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-mptt-admin/dist/django-mptt-admin-0.3.1.tar.gz
        fi
        if [ "$1" = "tinymce" ]; then
            cd $DIR/apps/django-tinymce
            python $DIR/apps/django-tinymce/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-tinymce/dist/django-tinymce-2.7.0.dev0.tar.gz
        fi
        if [ "$1" = "sortedm2m" ]; then
            cd $DIR/apps/django-sortedm2m
            python $DIR/apps/django-sortedm2m/setup.py sdist
            pip install --upgrade --no-deps --force-reinstall --ignore-installed $DIR/apps/django-sortedm2m/dist/django-sortedm2m-0.8.1.tar.gz
        fi
        if [ "$1" = "migrations" ]; then
            $DIR/hispaniae/manage.py makemigrations
            $DIR/hispaniae/manage.py migrate
        fi
    # Shift all the parameters down by one
    shift
done
cd $DIR/hispaniae

#$DIR/hispaniae/manage.py schemamigration opress --auto
#$DIR/hispaniae/manage.py schemamigration photologue --auto

$DIR/hispaniae/manage.py collectstatic --noinput
