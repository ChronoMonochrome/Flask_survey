from flask_wtf import FlaskForm
from flask_babel import lazy_gettext, gettext, ngettext
from wtforms import PasswordField, SubmitField, StringField, TextAreaField, SelectField, SubmitField
from .. import models

class SignupForm(FlaskForm):
	login = StringField(lazy_gettext("Login"))

	name = StringField(lazy_gettext("Name"))

	password = PasswordField(lazy_gettext('Password'))

	role = SelectField(lazy_gettext('Role'), choices = [
					('student', lazy_gettext('student')),
					('teacher', lazy_gettext('teacher')),
					('employee', lazy_gettext('employee'))
	])

	submit = SubmitField(lazy_gettext("Create account"))

	def __init__(self, *args, **kwargs):
		FlaskForm.__init__(self, *args, **kwargs)

	def validate(self):
		if not FlaskForm.validate(self):
			return False

		user = models.User.query.filter_by(login = self.login.data.lower()).first()
		if user:
			self.login.errors.append(lazy_gettext("That login is already taken"))
			return False
		else:
			return True

