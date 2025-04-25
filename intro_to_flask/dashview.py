#import glob
#from pathlib import Path, PurePath
from flask_babel import gettext, ngettext

from dash import Dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
#import pandas as pd

#p = Path('.')

class DashView:
	def __init__(self, server):
		self.server = server

	def Add_Dash(self, url, layout, css = None):
		"""Populates dash pages."""
		self.url_base_pathname = url
		self.layout = layout
		self.css = css
		self.dash_app = Dash(server = self.server, url_base_pathname = self.url_base_pathname)

		if self.css:
			self.dash_app.css.append_css(self.css)

		self.dash_app.layout = layout

		return self
