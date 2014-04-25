Initial commit 

Installation instructions 

checkout trunk into a gps directory on your django installation 
(gps/ dir should be right aside your project directory)

Edit your settings.py file and add 'gps' to your installed apps
edit your urls.py and add the line (r'^', include('gps.urls')),
(this is assuming the fact gps app is your site index but you could surely make it a subdirectory of your installation)

run

python manage.py syncdb

python manage.py runserver 

browse the app on localhost:8000 


Enjoy


