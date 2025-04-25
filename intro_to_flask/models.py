from collections import OrderedDict

from intro_to_flask import app
from wtforms import Field, DecimalField, IntegerField, FloatField, SelectField, StringField, TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField, DateField

#if __name__ == "__main":
from .widgets import DatePicker
#else:
#from widgets import DatePicker

from flask_babel import lazy_gettext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, BigInteger, Numeric, Float, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug import generate_password_hash, check_password_hash
from wtforms.validators import Required, Length

app.db = SQLAlchemy(app)

class MyField:
	def __init__(self, field_type, field_name, is_dropdown = False, foreign_model = None, foreign_key = "value", **kwargs):
		self.field_type = field_type
		self.field_name = field_name
		self.is_dropdown = is_dropdown
		if foreign_model:
			self.is_dropdown = True
		self.foreign_model = foreign_model
		self.foreign_key = foreign_key
		for k in kwargs:
			setattr(self, k, kwargs[k])


class ColumnRange(Column):
	def __init__(self, *args, **kwargs):
		self.range_start = kwargs.pop("range_start", 0)
		self.range_step = kwargs.pop("range_step", 1.0)
		self.range_end = kwargs.pop("range_end", 100)
		super(self.__class__, self).__init__(*args, **kwargs)

class ColumnFieldsBound(Column):
	def __init__(self, *args, **kwargs):
		self.fields = kwargs.pop("fields", None)
		if (not self.fields):
			raise ValueError("fields cannot be None")

		super(self.__class__, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.setup_field(field)

	def setup_field(self, field):
		field.field_kwargs = OrderedDict()
		field.field_kwargs["label"] = lazy_gettext(field.field_name)
		if (field.field_type == StringField):
			field.field_kwargs["validators"] = [Required(), Length(max = getattr(self.type, "length", 100))]
			field.field_kwargs["render_kw"] = {'maxlength': getattr(self.type, "length", 100)}
		elif (field.field_type == IntegerField):
			field.field_kwargs["validators"] = [Required()]
			field.field_kwargs["render_kw"] = {"type": "number", "min": getattr(field, "min", -(2**31)), "max": getattr(field, "max", 2**32-1)}
		elif (field.field_type == DecimalField):
			field.field_kwargs["validators"] = [Required()]
			field.field_kwargs["render_kw"] = {"max": 2**31-1}
			field.field_kwargs["places"] = 2
		elif (field.field_type == SelectField):
			field.field_kwargs["validators"] = [Required()]
			field.field_kwargs["coerce"] = int
		elif (field.field_type == DateField):
			field.field_kwargs["validators"] = [Required()]
			#pass
		elif (field.field_type == DatePicker):
			field.field_kwargs["validators"] = [Required()]
			field.field_kwargs["language"] = "ru"
		else:
			raise ValueError("No known binding for column type %s and field type %s" % (str(self.type), str(field.field_type)))

	def create_field(self, field):
		if (field.field_type == SelectField):
			print(field.field_name)
		return field.field_type(**field.field_kwargs)

class ModelFormBinder:
	def __init__(self, model):
		self.model = model

	def find_model_by_tablename(self, tablename):
		for clazz in app.db.Model._decl_class_registry.values():
			if getattr(clazz, "__tablename__", "") == tablename:
				return clazz

		return None

	def parse_model(self):
		elements = OrderedDict()
		for col in self.model.__table__.columns:
			if not (col.name.endswith("_from") or col.name.endswith("_up")):
				elements[col.name] = [col]
				continue
			range_name = col.name.replace("_from", "").replace("_up", "")
			if not range_name in elements:
				elements[range_name] = [col]
			else:
				elements[range_name].append(col)
		return elements

class User(app.db.Model):
	__tablename__ = "users"
	id		= Column(Integer, primary_key = True)
	login		= Column(String(120), unique=True)
	pwdhash		= Column(String(300))
	role		= Column(String(120))
	name		= Column(String(300))
	municipality    = Column(String(40))
	teachers_num	= Column(Integer)
	students 	= relationship("Student", uselist = False, backref = __tablename__)
	survey_schools 	= relationship("SurveySchool", backref = __tablename__)
	survey_parents 	= relationship("SurveyParents", backref = __tablename__)
	survey_teachers 	= relationship("SurveyTeachers", backref = __tablename__)
	student_id	= Column(Integer, ForeignKey("student.id"))
	teacher_id	= Column(Integer, ForeignKey("teacher.id"))
	employee_id	= Column(Integer, ForeignKey("employee.id"))

	def __init__(self, login, name, password, role, **kwargs):
		super(self.__class__, self).__init__(**kwargs)
		self.login = login.lower()
		self.name = name
		self.set_password(password)
		self.set_role(role)

	def set_password(self, password):
		self.pwdhash = generate_password_hash(password)

	def set_role(self, role):
		self.role = role

	def check_password(self, password):
		return check_password_hash(self.pwdhash, password)
		
class SurveySchool(app.db.Model):
	__tablename__ = "survey_school"
	id 		= Column(Integer, primary_key = True)
	user_id	= Column(Integer, ForeignKey("users.id"))
	a1 	= Column(Integer, default=0)
	a2 	= Column(Integer, default=0)
	a3 	= Column(Integer, default=0)
	a4 	= Column(Integer, default=0)
	a5 	= Column(Integer, default=0)
	a6 	= Column(Integer, default=0)
	a7 	= Column(Integer, default=0)
	a8 	= Column(Integer, default=0)
	a9 	= Column(Integer, default=0)
	a9 	= Column(Integer, default=0)
	a10	= Column(Integer, default=0)
	a11	= Column(Integer, default=0)
	a12	= Column(Integer, default=0)
	a13	= Column(Integer, default=0)
	a14	= Column(Integer, default=0)
	a15	= Column(Integer, default=0)
	a16	= Column(Integer, default=0)
	a17	= Column(Integer, default=0)
	a18	= Column(Integer, default=0)
	a19	= Column(Integer, default=0)
	a20	= Column(Integer, default=0)
	a21	= Column(Integer, default=0)
	a22	= Column(Integer, default=0)
	a23	= Column(Integer, default=0)
	a24	= Column(Integer, default=0)
	a25	= Column(Integer, default=0)
	a26	= Column(Integer, default=0)
	a27	= Column(Integer, default=0)
	a28	= Column(Integer, default=0)
	
class SurveyTeachers(app.db.Model):
	__tablename__ = "survey_teacher"
	id 		= Column(Integer, primary_key = True)
	user_id	= Column(Integer, ForeignKey("users.id"))
	a01 	= Column(Integer, default=1)
	a02 	= Column(Integer, default=1)
	a03 	= Column(Integer, default=1)
	a04 	= Column(Integer, default=1)
	a05 	= Column(Integer, default=1)
	a06 	= Column(Integer, default=1)
	a07 	= Column(Integer, default=1)
	a08 	= Column(Integer, default=1)
	a09 	= Column(Integer, default=1)
	a10 	= Column(Integer, default=1)
	a11 	= Column(Integer, default=1)
	a12 	= Column(Integer, default=1)
	a13 	= Column(Integer, default=1)
	a14 	= Column(Integer, default=1)
	a15 	= Column(Integer, default=1)
	a16 	= Column(Integer, default=1)
	a17 	= Column(Integer, default=1)
	a18 	= Column(Integer, default=1)
	a19 	= Column(Integer, default=1)
	a20 	= Column(Integer, default=1)
	a21 	= Column(Integer, default=1)
	a22 	= Column(Integer, default=1)

class SurveyParents(app.db.Model):
	__tablename__ = "survey_parents"
	id 		= Column(Integer, primary_key = True)
	user_id	= Column(Integer, ForeignKey("users.id"))
	a01_01 	= Column(Integer, default=5)
	a01_02 	= Column(Integer, default=5)
	a01_03 	= Column(Integer, default=5)
	a01_04 	= Column(Integer, default=5)
	a01_05 	= Column(Integer, default=5)
	a01_06 	= Column(Integer, default=5)
	a01_07 	= Column(Integer, default=5)
	a01_08 	= Column(Integer, default=5)
	a01_09 	= Column(Integer, default=5)
	a01_10 	= Column(Integer, default=5)
	a01_11 	= Column(Integer, default=5)
	a01_12 	= Column(Integer, default=5)
	a02_01 	= Column(Integer, default=5)
	a02_02 	= Column(Integer, default=5)
	a02_03 	= Column(Integer, default=5)
	a02_04 	= Column(Integer, default=5)
	a02_05 	= Column(Integer, default=5)
	a02_06 	= Column(Integer, default=5)
	a02_07 	= Column(Integer, default=5)
	a02_08 	= Column(Integer, default=5)
	a02_09 	= Column(Integer, default=5)
	a02_10 	= Column(Integer, default=5)
	a02_11 	= Column(Integer, default=5)
	a02_12 	= Column(Integer, default=5)
	a03_01 	= Column(Integer, default=5)
	a03_02 	= Column(Integer, default=5)
	a03_03 	= Column(Integer, default=5)
	a03_04 	= Column(Integer, default=5)
	a03_05 	= Column(Integer, default=5)
	a03_06 	= Column(Integer, default=5)
	a03_07 	= Column(Integer, default=5)
	a03_08 	= Column(Integer, default=5)
	a04_01 	= Column(Integer, default=5)
	a04_02 	= Column(Integer, default=5)
	a04_03 	= Column(Integer, default=5)
	a04_04 	= Column(Integer, default=5)
	a04_05 	= Column(Integer, default=5)
	a04_06 	= Column(Integer, default=5)
	a04_07 	= Column(Integer, default=5)
	a04_08 	= Column(Integer, default=5)
	a05_01 	= Column(Integer, default=5)
	a05_02 	= Column(Integer, default=5)
	a05_03 	= Column(Integer, default=5)
	a05_04 	= Column(Integer, default=5)
	a05_05 	= Column(Integer, default=5)
	a05_06 	= Column(Integer, default=5)
	a05_07 	= Column(Integer, default=5)
	a05_08 	= Column(Integer, default=5)
	a06_01 	= Column(Integer, default=5)
	a06_02 	= Column(Integer, default=5)
	a06_03 	= Column(Integer, default=5)
	a06_04 	= Column(Integer, default=5)
	a06_05 	= Column(Integer, default=5)
	a06_06 	= Column(Integer, default=5)
	a06_07 	= Column(Integer, default=5)
	a06_08 	= Column(Integer, default=5)
	a07_01 	= Column(Integer, default=5)
	a07_02 	= Column(Integer, default=5)
	a07_03 	= Column(Integer, default=5)
	a07_04 	= Column(Integer, default=5)
	a07_05 	= Column(Integer, default=5)
	a07_06 	= Column(Integer, default=5)
	a07_07 	= Column(Integer, default=5)
	a08_01 	= Column(Integer, default=5)
	a08_02 	= Column(Integer, default=5)
	a08_03 	= Column(Integer, default=5)
	a08_04 	= Column(Integer, default=5)
	a08_05 	= Column(Integer, default=5)
	a08_06 	= Column(Integer, default=5)
	a09_01 	= Column(Integer, default=5)
	a09_02 	= Column(Integer, default=5)
	a09_03 	= Column(Integer, default=5)
	a09_04 	= Column(Integer, default=5)
	a09_05 	= Column(Integer, default=5)
	a09_06 	= Column(Integer, default=5)
	a09_07 	= Column(Integer, default=5)
	a09_08 	= Column(Integer, default=5)
	a09_09 	= Column(Integer, default=5)
	a09_10 	= Column(Integer, default=5)
	a09_11 	= Column(Integer, default=5)
	a10_01 	= Column(Integer, default=5)
	a10_02 	= Column(Integer, default=5)
	a10_03 	= Column(Integer, default=5)
	a10_04 	= Column(Integer, default=5)
	a10_05 	= Column(Integer, default=5)

class Student(app.db.Model):
	__tablename__ = "student"
	id				= Column(Integer, primary_key = True)
	user				= relationship("User", uselist = False, backref = __tablename__)
	student_competition_id	= Column(Integer, ForeignKey("student_competition.id"))
	municipality_id			= ColumnFieldsBound(Integer, ForeignKey("municipality.id"), fields = [MyField(field_type = SelectField, field_name = "municipality_id", foreign_model = "Municipality", foreign_key = "name_of_municipality")])
	organization_id			= ColumnFieldsBound(Integer, ForeignKey("organization.id"), fields = [MyField(field_type = SelectField, field_name = "organization_id",  foreign_model = "Organization", foreign_key = "name")])
	settlement_type_id		= ColumnFieldsBound(Integer, ForeignKey("settlement_type.id"), fields = [MyField(field_type = SelectField, field_name = "settlement_type_id",  foreign_model = "SettlementType")])
	level_educational_organization_id	= ColumnFieldsBound(Integer, ForeignKey("level_educational_organization.id"),
							fields = [MyField(field_type = SelectField, field_name = "level_educational_organization_id", foreign_model = "EduOrganizationLevel")])
	surname				= ColumnFieldsBound(String(50), fields = [MyField(field_type = StringField, field_name = "surname")])
	name				= ColumnFieldsBound(String(50), fields = [MyField(field_type = StringField, field_name = "name")])
	middle_name			= ColumnFieldsBound(String(40), fields = [MyField(field_type = StringField, field_name = "middle_name")])
	age_range_id			= ColumnFieldsBound(Integer, ForeignKey("age_range.id"), fields = [MyField(field_type = SelectField, field_name = "age_range_id", foreign_model = "AgeRange")])
	teaching_experience_range_id	= ColumnFieldsBound(Integer, ForeignKey("teaching_experience_range.id"), fields = [MyField(field_type = SelectField, field_name = "teaching_experience_range_id", foreign_model = "TeachingExperienceRange")])
	work_experience_subject_range_id	= ColumnFieldsBound(Integer, ForeignKey("work_experience_subject_range.id"), fields = [MyField(field_type = SelectField, field_name = "work_experience_subject_range_id", foreign_model = "WorkExperienceSubjectRange")])
	total_load_range_id			= ColumnFieldsBound(Integer, ForeignKey("total_load_range.id"), fields = [MyField(field_type = SelectField, field_name = "total_load_range_id", foreign_model = "TotalLoadRange")])
	load_on_subject_range_id		= ColumnFieldsBound(Integer, ForeignKey("load_on_subject_range.id"), fields = [MyField(field_type = SelectField, field_name = "load_on_subject_range_id", foreign_model = "LoadOnSubjectRange")])
	number_of_subjects_taught	= ColumnFieldsBound(Integer,
						fields = [MyField(field_type = IntegerField, field_name = "number_of_subjects_taught", min = 0, max = 7)])
	education_type_id		= ColumnFieldsBound(Integer, ForeignKey("education_type.id"), fields = [MyField(field_type = SelectField, field_name = "education_type_id", foreign_model = "EducationType")])
	category_id			= ColumnFieldsBound(Integer, ForeignKey("category.id"), fields = [MyField(field_type = SelectField, field_name = "category_id", foreign_model = "EduCategory")])
	retraining_institution_id	= ColumnFieldsBound(Integer, ForeignKey("retraining_institution.id"), fields = [MyField(field_type = SelectField, field_name = "retraining_institution_id", foreign_model = "RetrainingInstitution")])
	retraining_date_id		= ColumnFieldsBound(Integer, ForeignKey("retraining_date.id"), fields = [MyField(field_type = SelectField, field_name = "retraining_date_id", foreign_model = "RetrainingDate")])
	training_institution_id		= ColumnFieldsBound(Integer, ForeignKey("training_institution.id"), fields = [MyField(field_type = SelectField, field_name = "training_institution_id", foreign_model = "TrainingInstitution")])
	training_date_id		= ColumnFieldsBound(Integer, ForeignKey("training_date.id"), fields = [MyField(field_type = SelectField, field_name = "training_date_id", foreign_model = "TrainingDate")])

	def __init__(self, **kwargs):
		super(self.__class__, self).__init__(**kwargs)
		
class StudentCompetition(app.db.Model):
	__tablename__ = "student_competition"
	id = Column(Integer, primary_key = True)
	student = relationship("Student",  uselist = False, backref = __tablename__)
	predmet_n1 = Column(Integer)
	predmet_n2 = Column(Integer)
	predmet_n3 = Column(Integer)
	predmet_n4 = Column(Integer)
	predmet_n5 = Column(Integer)
	predmet_n6 = Column(Integer)
	metod_n7 = Column(Integer)
	metod_n8 = Column(Integer)
	metod_n9 = Column(Integer)
	psy_ped_n10 = Column(Integer)
	communication_n11 = Column(Integer)
	

class Teacher(app.db.Model):
	__tablename__ = "teacher"
	id				= Column(Integer, primary_key = True)
	user				= relationship("User", uselist = False, backref = __tablename__)
	
class Employee(app.db.Model):
	__tablename__ = "employee"
	id				= Column(Integer, primary_key = True)
	user				= relationship("User", uselist = False, backref = __tablename__)

class Municipality(app.db.Model):
	__tablename__ = "municipality"
	id			= Column(Integer, primary_key = True)
	organizations 		= relationship("Organization", backref = __tablename__)
	students 		= relationship("Student", backref = __tablename__)
	name_of_municipality	= ColumnFieldsBound(String(50), fields = [MyField(field_type = StringField, field_name = "name_of_municipality")])

class Organization(app.db.Model):
	__tablename__ = "organization"
	id			= Column(Integer, primary_key = True)
	municipality_id		= Column(Integer, ForeignKey("municipality.id"))
	inn			= ColumnFieldsBound(BigInteger, unique=True, fields=[MyField(field_type = IntegerField, field_name = "inn")])
	address			= ColumnFieldsBound(String(256), fields = [MyField(field_type = StringField, field_name = "address")])
	name			= ColumnFieldsBound(String(256), fields = [MyField(field_type = StringField, field_name = "name")])
	short_name		= ColumnFieldsBound(String(256), fields = [MyField(field_type = StringField, field_name = "short_name")])
	latitude		= ColumnFieldsBound(String(30), fields = [MyField(field_type = StringField, field_name = "latitude")])
	longitude		= ColumnFieldsBound(String(30), fields = [MyField(field_type = StringField, field_name = "longitude")])
	license_num		= ColumnFieldsBound(String(256), fields = [MyField(field_type = StringField, field_name = "license_num")])
	license_status		= ColumnFieldsBound(String(256), fields = [MyField(field_type = StringField, field_name = "license_status")])
	license_details		= ColumnFieldsBound(String(256), fields = [MyField(field_type = StringField, field_name = "license_details")])

class AgeRange(app.db.Model):
	__tablename__ = "age_range"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(40))

class SettlementType(app.db.Model):
	__tablename__ = "settlement_type"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(40))

class EduOrganizationLevel(app.db.Model):
	__tablename__ = "level_educational_organization"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(40))

class EducationType(app.db.Model):
	__tablename__ = "education_type"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(40))

class EduCategory(app.db.Model):
	__tablename__ = "category"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(20))

class TeachingExperienceRange(app.db.Model):
	__tablename__ = "teaching_experience_range"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(50))

class WorkExperienceSubjectRange(app.db.Model):
	__tablename__ = "work_experience_subject_range"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(50))

class TotalLoadRange(app.db.Model):
	__tablename__ = "total_load_range"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(40))

class LoadOnSubjectRange(app.db.Model):
	__tablename__ = "load_on_subject_range"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(50))

class TrainingInstitution(app.db.Model):
	__tablename__ = "training_institution"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(100))

class TrainingDate(app.db.Model):
	__tablename__ = "training_date"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(100))

class RetrainingInstitution(app.db.Model):
	__tablename__ = "retraining_institution"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(100))

class RetrainingDate(app.db.Model):
	__tablename__ = "retraining_date"
	id = Column(Integer, primary_key = True)
	students = relationship("Student", backref = __tablename__)
	value = Column(String(100))

app.db.create_all()
