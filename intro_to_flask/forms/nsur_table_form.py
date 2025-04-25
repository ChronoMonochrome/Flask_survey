from flask_wtf import FlaskForm
from flask_babel import lazy_gettext, gettext, ngettext
from wtforms import PasswordField, Form, FormField, FieldList, HiddenField, SubmitField, IntegerField, StringField, TextAreaField, SelectField, SubmitField, validators, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from . import slick_grid_form

from .. import views
from .. import widgets

class NsurTableForm(FlaskForm, slick_grid_form.SlickGridForm):
	myGrid = widgets.SlickGrid("myGrid", style={"width": "100%", "height": "500px"})
	submit = SubmitField(lazy_gettext("Save"))
	data = HiddenField("data")
	def __init__(self, *args, **kwargs):
		FlaskForm.__init__(self, *args, **kwargs)
		self.view = views.StudentView()

		# self.view must be initialized
		slick_grid_form.SlickGridForm.__init__(self)