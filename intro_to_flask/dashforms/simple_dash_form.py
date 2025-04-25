from intro_to_flask import app
from flask_babel import gettext, ngettext

import dash_table
import dash_core_components as dcc
import dash_html_components as html

from .. import dashview

class SimpleDashForm:
	def __init__(self, url):
		self.dashview = dashview.DashView(app)

		layout = html.Div(children=[
			html.H1(children=gettext('Hello Dash')),
			html.Div(children='''
				      %s
				''' % gettext("Dash: A web application framework for Python.")),
			html.Br()
		])

		self.form = self.dashview.Add_Dash(url, layout = layout, css = {
		        "external_url": "https://derp.sfo2.digitaloceanspaces.com/style.css"
		})


form = SimpleDashForm("/dataview/").form

__all__ = [form]
