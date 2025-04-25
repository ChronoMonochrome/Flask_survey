import os
import errno

import dateutil
from time import time

from collections import OrderedDict

from flask import render_template_string
from flask_wtf import FlaskForm
from flask_babel import gettext, lazy_gettext, ngettext
from wtforms import Field, DecimalField, IntegerField, SelectField, StringField, TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField

from .widgets import BootstrapSlider, DatePicker

from wtforms.validators import Required, Length

from . import models

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Numeric, Float, String, DateTime, ForeignKey, Table
from .models import ColumnFieldsBound, ModelFormBinder

class FormFactory:
	def __init__(self, app):
		self.app = app
		self.def_template_path = os.path.join(app.config["TEMPLATES_DIR"], "forms_factory.html")
		if not os.path.isfile(self.def_template_path):
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.def_template_path)

		self.entry_ptr = """    {{{{ form.{name}.label }}}}\n""" + \
				 """    {{{{ form.{name}(value = {name}_def_value) }}}}\n"""

		self.slider_ptr = """   {{{{ form.{name} }}}}\n"""

		self.javascript_ptr = """$(document).ready(function() {{ {sliders_js} {datepickers_js} {custom_js} }});"""
		self.slider_js_ptr = """
        $("#{name}").slider({{
            min  : {min},
            max  : {max},
            value: [ {min_value}, {max_value} ],
            focus: false
        }});
        var {name}_orig;
        $("#{name}").on('slideStart', function(slideEvt){{
            {name}_orig = $('#{name}').data('slider').getValue();
        }});
        $("#{name}").on('slideStop', function(slideEvt){{
            var {name}_new = $('#{name}').data('slider').getValue();
            if ({name}_orig[0] != {name}_new[0]) {{
                //console.log("stop slide");
                slideEvt.value[1] = slideEvt.value[0] + {step};
                $("#{name}").slider("setValue", slideEvt.value);
            }}
            if ({name}_orig[1] != {name}_new[1]) {{
                //console.log("stop slide");
                slideEvt.value[0] = slideEvt.value[1] - {step};
                $("#{name}").slider("setValue", slideEvt.value);
            }}
        }});
        """

		self.datepicker_js_ptr = """
	$("#{name}").datepicker({{
                 language: "{language}"
        }});
	"""

	def default_constructor(self):
		pass

	def create_form(self, model, form_title, route_url, constructor_func = None, custom_js = [], hide_header = False):
		def on_submit(self):
			for col_name, col_vals in self.ModelFormBinder.parse_model().items():
				entry_name = col_name
				if entry_name == "id" or entry_name.endswith("_id"):
					continue

				if len(col_vals) > 1:
					try:
						vals = eval(getattr(self, entry_name).data)
					except:
						print("got error during eval(\"%s\")" % getattr(self, entry_name).data)
						vals = [0, 20]

					#print("set %s.%s = %s" % (self.model, entry_name + "_from", vals[0]))
					setattr(self.model, entry_name + "_from", vals[0])
					#print("set %s.%s = %s" % (self.model, entry_name + "_up", vals[1]))
					setattr(self.model, entry_name + "_up", vals[1])
					continue

				col = col_vals[0]

				if type(col.type) == String:
					val = getattr(self, entry_name).data
					if (type(val) == str):
						val = val[:col.type.length]
				elif type(col.type) == Integer:
					val = getattr(self, entry_name).data
					if type(val) == str and val.isdigit():
						val = min(int(val), (2**31-1))
				else:
					if (type(col) == Column):
						val = getattr(self, entry_name).data
					elif (type(col) == ColumnFieldsBound):
						field = col.fields[0]
						if field.field_type == DatePicker:
							val = str(dateutil.parser.parse(getattr(self, entry_name).data))
						else:
							val = getattr(self, entry_name).data

				print("set %s.%s = %s" % (str(self.model), entry_name, str(val)))

				# TODO: some more sanity validation?
				setattr(self.model, entry_name, val)

		def on_render(self):
			def_values = dict()
			# TODO: default slider values shouldn't be passed to render_template_string
			for col in self.model.__table__.columns:
				entry_name = col.name
				val = getattr(self.model, entry_name)
				if not val:
					continue
				def_values["%s_def_value" % entry_name] = val

			return render_template_string(self.template_str, form = self, hide_header = hide_header, **def_values)

		class_name = model.__class__.__name__

		form_template_str = open(self.def_template_path, "r").read()

		attributes = OrderedDict()
		model_form_binder = ModelFormBinder(model)
		attributes["ModelFormBinder"] = model_form_binder
		form_elements = []
		sliders_js = []
		datepickers_js = []
		choices = OrderedDict()

		if not constructor_func:
			constructor_func = self.default_constructor

		#attributes["__init__"] = constructor_func

		#print(parse_model(model))

		for col_name, col_vals in model_form_binder.parse_model().items():
			class_attr_name = col_name
			col_label_id = col_name
			if col_label_id == "id":
				continue

			#if col_label_id.endswith("_id"):
			#	continue

			if len(col_vals) > 1:
				slider_val = [0, 0]
				tmp = getattr(model, col_vals[0].name, 0)
				if tmp:
					slider_val[0] = tmp
				tmp = getattr(model, col_vals[1].name, 0)
				if tmp:
					slider_val[1] = tmp

				slider_step = getattr(col_vals[0], "range_step", .1)
				range_start = getattr(col_vals[0], "range_start", 0)
				range_end = getattr(col_vals[1], "range_end", 1)

				class_attr_val = BootstrapSlider(gettext(class_attr_name), def_min = range_start, def_max = range_end, def_step = slider_step)

				try:
					sliders_js.append(self.slider_js_ptr.format(
					     name = class_attr_name,
					     min = range_start,
					     max = range_end,
					     min_value = max(slider_val[0], range_start),
					     max_value = min(slider_val[1], range_end),
					     step = slider_step
					))
				except:
					print(slider_val[0], range_start)
					print(slider_val[1], range_end)
					raise

				attributes[class_attr_name] = class_attr_val
				#print(self.slider_ptr.format(name = col_label_id))
				#print(col_label_id)
				form_elements.append(self.entry_ptr.format(name = col_label_id))
				continue

			col = col_vals[0]

			if (type(col) == ColumnFieldsBound):
				for field in col.fields:
					class_attr_name = field.field_name
					class_attr_val = col.create_field(field)
					col_label_id = field.field_name
					#if field.field_type == SelectField:
					#	continue
					if field.is_dropdown: # and class_attr_name == "age_range_id":
						#print("assigning %s choices" % class_attr_name)
						choices[class_attr_name] =  [(o.id, getattr(o, field.foreign_key)) for o in getattr(models, field.foreign_model).query.order_by('id')]

					attributes[class_attr_name] = class_attr_val
					form_elements.append(self.entry_ptr.format(name = col_label_id))
					if field.field_type == DatePicker:
						language = field.field_kwargs.get("language", "en")
						datepickers_js.append(self.datepicker_js_ptr.format(
							name = class_attr_name,
							language = language
						))

		#attributes["ex16b"] = BootstrapSlider("TestSlider")
		#attributes["ex16b1"] = BootstrapSlider("TestSlider")

		attributes["submit"] = SubmitField(lazy_gettext("Submit"))
		attributes["on_submit"] = on_submit
		attributes["on_render"] = on_render

		javascript_str = self.javascript_ptr.format(
				sliders_js = "\n".join(sliders_js),
				datepickers_js = "\n".join(datepickers_js),
				custom_js = "\n".join(custom_js)
		)
		#print(javascript_str)
		attributes["javascript_str"] = javascript_str

		form_template_str = form_template_str.format(title = form_title,
			url_for = route_url,
			time = time(),
			javascript_str = javascript_str,
			form_elements = "\n".join(form_elements))

		attributes["template_str"] = form_template_str
		#print(form_template_str)
		attributes["model"] = model

		NewClass = type(class_name, (FlaskForm,), attributes)()
		for class_attr_name, choice_vals in choices.items():
			setattr(getattr(NewClass, class_attr_name), "choices", choice_vals)
		#NewClass.age_range_id.choices = []

		return NewClass
