from intro_to_flask import app
from flask_babel import gettext, ngettext

from dash.dependencies import Input, Output
from .. import dashview
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

class ProfileForm:
	def __init__(self, url):
		self.dashview = dashview.DashView(app)

		params = [
		    'Weight', 'Torque', 'Width', 'Height',
		    'Efficiency', 'Power', 'Displacement'
		]

		self.layout = html.Div([
			dash_table.DataTable(
				id='table-editing-simple',
				columns=(
				    [{'id': 'Model', 'name': 'Model'}] +
				    [{'id': p, 'name': p} for p in params]
				),
				data=[
				    dict(Model=i, **{param: 0 for param in params})
				    for i in range(1, 5)
				],
				editable=True
			),
			dcc.Graph(id='table-editing-simple-output')
		])

		self.form = self.dashview.Add_Dash(url, layout = self.layout)

form = ProfileForm("/another_editing_form/")
dash_app = form.dashview.dash_app
form = form.form

@dash_app.callback(
    Output('table-editing-simple-output', 'figure'),
    [Input('table-editing-simple', 'data'),
     Input('table-editing-simple', 'columns')])
def display_output(rows, columns):
	df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
	return {
	    'data': [{
	        'type': 'parcoords',
	        'dimensions': [{
	            'label': col['name'],
	            'values': df[col['id']]
	        } for col in columns]
	    }]
	}

__all__ = [form]
