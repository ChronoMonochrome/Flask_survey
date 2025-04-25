#!/usr/bin/env python3

from flask_failsafe import failsafe

@failsafe
def main():
	from intro_to_flask import app
	return app

if __name__ == "__main__":
	main().run(debug=True, host="0.0.0.0", port=8011)
