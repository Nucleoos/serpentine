Checkout trunk if you need the entire django serpentine project 
It contains settings.py you will have to reajust to your personnal settings (db + path to your files). The checkout initiate a small sqlite database with few tracks. Few samples gpx files are in the media/ folder

If you already have a django project - just checkout the "/trunk/gps/" into a gps folder under your django project part onto your installation. 
You will have to add 'gps' app and urls to your settings and then run "syncdb" to create the tables. I'll write a special wiki part later to ease this part. 



= Liste des petites et grandes choses à traiter =

== Fonctionnalités ==

  * Page _gérer mes traces_ (ajouter-supprimer-modifier) 
  * Index complet des traces
  * Vraie page d'accueil
  * Scorer les traces 
  * Gérer les segments de traces 
  * Ajouter des photos dans la trace (click droit ajouter)
  * Repérer les segments analogues
