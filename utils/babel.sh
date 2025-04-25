pybabel extract -F intro_to_flask/babel.cfg -k lazy_gettext -o intro_to_flask/messages.pot intro_to_flask
pybabel update -i intro_to_flask/messages.pot -d intro_to_flask/translations
