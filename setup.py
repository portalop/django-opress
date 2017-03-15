import os
from setuptools import setup, find_packages

#README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='opress',
    version='0.1',
    packages=find_packages(),
    license='BSD License',  # example license
    description='A simple Django app to create static pages.',
#    long_description=README,
    url='http://www.dominicos.org/',
    author='Oficina Internet Dominicos',
    author_email='portalop@dominicos.org',
    include_package_data=True,
    package_data={
        'opress': [
            'static/opress/js/*.js',
            'static/colorbox/js/*.js',
            'static/colorbox/css/*.css',
            'static/colorbox/images/*.*',
        ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)