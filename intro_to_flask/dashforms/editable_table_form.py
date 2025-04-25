# -*- coding: UTF-8 -*-

from intro_to_flask import app
from flask_babel import gettext, ngettext, lazy_gettext
from flask import url_for, session

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from .. import dashview
from .. import models

from .. import views
MyColumn = views.MyColumn

import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from collections import OrderedDict
import pprint

to_str = lambda x: str(x) if x else ""
to_int = lambda x: int(x) if x else 0

class MyStr(str):
	def __init__(self, value):
		#print(value)
		self.value = value

	def __repr__(self):
		return str(self.value)

	def __str__(self, value):
		return self.__repr__()

class EditableTableForm:
	def __init__(self, url):
		self.dashview = dashview.DashView(app)
		self.view = views.StudentView()
		self.table_data = OrderedDict()
		self.dash_columns = []
		self.column_conditional_dropdowns = []
		self.dropdown_tpl = lambda col_name: {
					# column id
					'id': col_name,
					'dropdowns': [
						{
					   		# these are filter strings
							'condition': 'id eq "{}"'.format(str(row.id)),
							'dropdown': [
								{'label': i, 'value': i}
								for i in self.view.columns[col_name].choices
							]
						} for row in self.data
					]
				}

		#print(self.column_conditional_dropdowns)
		#print("hi")
		self.on_form_update()
				
		self.layout = html.Div([
			html.Div(
				dash_table.DataTable(
					id='dropdown_per_row',
					#columns=self.dash_columns,
					#data=self.table_data,
					#data=self.dash_table_data,
					editable=True,
					#row_selectable = "single",
					#style_table={'overflowX': 'scroll'},
					#style_cell={
					#	'minWidth': '0px', 'maxWidth': '180px',
					#	'whiteSpace': 'no-wrap',
					#	'overflow': 'hidden',
					#	'textOverflow': 'ellipsis',
					#},
					css=[{
						'selector': '.dash-cell div.dash-cell-value',
						'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
					}],
					column_conditional_dropdowns = self.column_conditional_dropdowns
				),
				style={
					'overflowX': 'scroll'
				}
			), 

			html.Br(),
			html.Div(id='placeholder'),
			html.Button('Сохранить', id='save-button'),
			html.Button('Отменить', id='dismiss-button'),
		])

		self.form = self.dashview.Add_Dash(url, layout = self.layout)
		
	def on_form_update(self):
		self.data = self.view.model.query.all()
		#print(self.data)
		col_val = lambda row: getattr(row, col_name)
		
		self.dash_columns = []
		
		for col_name, column in self.view.columns.items():
			if column.is_dropdown:
				self.column_conditional_dropdowns.append(self.dropdown_tpl(col_name))
				self.dash_columns.append({'id': col_name, 'name': gettext(col_name), 'presentation': 'dropdown'})
			elif col_name == "id":
				self.dash_columns.append({'id': col_name, 'name': gettext(col_name)})
			else:
				self.dash_columns.append({'id': col_name, 'name': gettext(col_name)})

		for col_name, column in self.view.columns.items():
			if column.is_dropdown:
				try:
					new_val = [column.choices_pair_kv.get(col_val(row), "") for row in self.data]
					self.table_data[col_name] = new_val
				except:
					print(col_name)
					print(column.choices_pair_kv)
					raise

			elif col_name == "id":
				self.table_data[col_name] = [to_str(getattr(i, col_name)) for i in self.data]
			else:
				self.table_data[col_name] = [column.eval(getattr(i, col_name)) for i in self.data]

		self.dash_table_data = pd.DataFrame(self.table_data).to_dict('rows')
		#print(self.dash_table_data)

	def on_submit(self, data):
		for n, row in enumerate(data):
			student = self.view.model.query.filter_by(id = row["id"]).first()
			for col_name, val in row.items():
				if col_name == "id":
					continue
				column = self.view.columns[col_name]
				if column.is_dropdown:
					val = column.dropdown_val_to_index(val)
				print("set %s.%s = %s" % (str(student), col_name, str(val)))
				setattr(student, col_name, val)
		app.db.session.commit()


dash_form = EditableTableForm("/profile_form/")
form = dash_form.form

@form.dash_app.callback(Output('placeholder', 'children'),
				  [Input('save-button', 'n_clicks'),
				   Input('dropdown_per_row', 'data')])
def on_save(n_clicks, table_data):
	if n_clicks is None:
		# Preventing the None callbacks is important with the store component,
		# you don't want to update the store for nothing.
		return ""

	dash_form.on_submit(table_data)

	return "test"

@form.dash_app.callback(Output('dropdown_per_row', 'data'),
				  [Input('dismiss-button', 'n_clicks')])
def output_to_table_data(dismiss_clicks):
	#if m_ts is None:
	#	raise PreventUpdate
		
	#print(m_ts)
	#if renew_clicks is not None:
	#print(data)

	dash_form.on_form_update()
	return dash_form.dash_table_data
	
@form.dash_app.callback(Output('dropdown_per_row', 'columns'),
				  [Input('dismiss-button', 'n_clicks')])
def output_to_table_columns(n_clicks):
	#if ts is None:
	#	raise PreventUpdate	

	dash_form.on_form_update()
	return dash_form.dash_columns

__all__ = [form]
