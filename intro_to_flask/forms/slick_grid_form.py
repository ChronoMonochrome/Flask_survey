from intro_to_flask import app

from collections import OrderedDict
import pandas as pd

from .. import views

class MyForm:
	def __init__(self):
		pass
		
	def get_data(self):
		res = app.db.session.query(*([self.view.model] + self.view.other_models)).join(*self.view.other_models).all()
		self._data = []
		for row in res:
			row_dict = OrderedDict()
			row_dict["id"] = row[0].id
			for model in row:
				for col_name, column in model.__table__.columns.items():
					if col_name == "id":
						continue
					row_dict[col_name] = getattr(model, col_name)
			self._data.append(row_dict)
		return self._data
		
	def set_data(self, data):
		for row in data:
			models = app.db.session.query(*([self.view.model] + self.view.other_models)).join(*self.view.other_models).filter_by(id = row["id"]).first()
			qmodels = OrderedDict([(type(i), i) for i in models])
			#print(self.view.column2model["name"])
			for col_name, val in row.items():
				if col_name == "id":
					continue
					
				model_obj = qmodels[self.view.column2model[col_name]]
				print("set %s.%s = %s" % (str(model_obj), col_name, str(val)))
				setattr(model_obj, col_name, val)
		app.db.session.commit()

class SlickGridForm(MyForm):
	def __init__(self, **kwargs):
		self.view.slick_columns = []
		for col_id, col in self.view.columns.items():
			if type(col) != views.SlickGridColumn:
				continue

			self.view.slick_columns.append(col.slick_kwargs)
		self.view.table_data = OrderedDict()

	def on_update(self):
		self.get_data()
		#print(self.view.data)
		col_val = lambda row: getattr(row, col_name)

		#print(len(self._data))
		for col_name, column in self.view.columns.items():
			if column.is_dropdown:
				self.view.table_data[col_name] = [row[col_name] for row in self._data]

			elif col_name == "id":
				self.view.table_data[col_name] = [views.to_str(row[col_name]) for row in self._data]
			else:
				self.view.table_data[col_name] = [column.eval(row[col_name]) for row in self._data]

		#print(self.view.table_data)
		self.view.table_data = pd.DataFrame(self.view.table_data).to_dict('rows')

	def on_submit(self, data):
		self.set_data(data)
