from intro_to_flask import app

from collections import OrderedDict

from flask_babel import gettext, ngettext, lazy_gettext
import pandas as pd
from . import models

to_str = lambda x: str(x) if x else ""
to_int = lambda x: int(x) if x else 0

class MyColumn:
	type_to_eval = {int: to_int, str: to_str}

	def __init__(self, type, is_dropdown = False, foreign_model = None, foreign_key= "value", set_choices_on_init = True, filter_by_params = {}):
		if not type in self.type_to_eval:
			raise ValueError("type %s is not supported" % str(type))

		self.eval = self.type_to_eval[type]
		self.is_dropdown = is_dropdown
		self.foreign_model = foreign_model
		self.foreign_key = foreign_key
		self.filter_by_params = filter_by_params
		self.set_choices_on_init = set_choices_on_init
		if (is_dropdown):
			self.set_dropdown_choices()

	def dropdown_val_to_index(self, value):
		if not self.is_dropdown:
			raise ValueError("column is not dropdown")
		return self.choices_pair_vk[value]

	def set_dropdown_choices(self, dataSource = None):
		self.choices_pair_kv = OrderedDict()
			
		if self.set_choices_on_init:
			self.choices_pair_kv = OrderedDict([
				(o.id, getattr(o, self.foreign_key)) for o in getattr(models, self.foreign_model).query.filter_by(**self.filter_by_params).order_by('id')
			])
		elif dataSource:
			self.choices_pair_kv = dataSource

		self.choices_pair_vk = OrderedDict([
			(v,k) for k,v in self.choices_pair_kv.items()
		])
		self.choices_indices = list(self.choices_pair_kv.keys())
		self.choices = list(self.choices_pair_kv.values())
		
class SlickGridColumn(MyColumn):
	def __init__(self, id, type, **kwargs):
		slick_defaults = {
			"name": lazy_gettext(id),
			"field": id,
			"width": 100,
			"minWidth": None,
			"maxWidth": None,
			"columnGroup": None,
			"cssClass": None,
			"formatter": None,
			"editor": None,
			"validator": None,
			"dataSource": None,
			"set_choices_on_cell_change": (True if kwargs.get("editor") == "Select3Editor" else None),
			"query_dropdown_filter_key": None,
			"query_dropdown_filter_model": None,
			"query_dropdown_api_url": None,
			"query_dropdown_key": None
		}

		self.id = id
		self.slick_kwargs = dict()
		for key, val in slick_defaults.items():
			passed_arg_val = kwargs.pop(key, None)

			# no value passed by user and no default set
			if passed_arg_val is None and val is None:
				continue

			# value passed by user, override default
			if passed_arg_val is not None:
				self.slick_kwargs[key] = passed_arg_val
				continue

			# no value passed by user but default set
			if passed_arg_val is None and val is not None:
				self.slick_kwargs[key] = val
		super(self.__class__, self).__init__(type, **kwargs)
		
		is_dropdown = kwargs.get("is_dropdown", False)
		if is_dropdown:
			dataSource = self.slick_kwargs.get("dataSource")
			editor = self.slick_kwargs.get("editor")
			if editor == "Select3Editor":
				required_params = ["foreign_model", "foreign_key"]
				required_slick_params = ["query_dropdown_filter_key", "query_dropdown_filter_model"]
				for param in required_params:
					if not param in kwargs:
						raise ValueError("%s parameter must be specified for editor %s" % (param, editor))
					globals()[param] = kwargs.get(param)
						
				for param in required_slick_params:
					if not param in self.slick_kwargs:
						raise ValueError("%s parameter must be specified for editor %s" % (param, editor))
					globals()[param] = self.slick_kwargs.get(param)
					
				model = getattr(models, foreign_model)
				filter_model = getattr(models, query_dropdown_filter_model)
				dataSource = {
								id: 
								{
									o.id: getattr(o, foreign_key)
										for o in model.query.filter_by(**{query_dropdown_filter_key: id})
								} for id in [o.id for o in filter_model.query.all()]
							 }
				self.slick_kwargs["select3_dataSource"] = dataSource
			elif dataSource is not None:
				self.set_dropdown_choices(dataSource)
				#print(dataSource)
			
			self.slick_kwargs["dataSource"] = self.choices_pair_kv
			
class MyView:
	def __init__(self):
		self.column2model = OrderedDict()
		for col_name in self.columns:
			found = False
			for model in [self.model] + self.other_models:
				if col_name in dir(model):
					found = True
					break
			if not found:
				raise ValueError("column %s was not found in any view models")
				
			self.column2model[col_name] = model

class StudentView(MyView):
	def __init__(self, **kwargs):
		self.model = models.Student
		self.other_models = [models.StudentCompetition]

		self.columns = OrderedDict([
			("id", SlickGridColumn(id = "id", type=int, **{"width": 40, "cssClass": "cell-title", "validator": "requiredFieldValidator"})),
			("municipality_id", SlickGridColumn(id = "municipality_id", type=str, is_dropdown = True, foreign_model = "Municipality", foreign_key = "name_of_municipality", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("organization_id", SlickGridColumn(id = "organization_id", type=str, is_dropdown = True, foreign_model = "Organization", foreign_key = "name", **{"minWidth": 300, "formatter": "Select3Formatter",  "editor": "Select3Editor",  "query_dropdown_filter_model": "Municipality", "query_dropdown_filter_key": "municipality_id"})),
			("settlement_type_id", SlickGridColumn(id = "settlement_type_id", type=str, is_dropdown = True, foreign_model = "SettlementType", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("level_educational_organization_id", SlickGridColumn(id = "level_educational_organization_id", type=str, is_dropdown = True, foreign_model = "EduOrganizationLevel", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("surname", SlickGridColumn(id = "surname", type=str, **{"width": 100, "editor": "Slick.Editors.Text"})),
			("name", SlickGridColumn(id = "name", type=str, **{"width": 100, "editor": "Slick.Editors.Text"})),
			("middle_name", SlickGridColumn(id = "middle_name", type=str, **{"width": 100, "editor": "Slick.Editors.Text"})),
			("number_of_subjects_taught", SlickGridColumn(id = "number_of_subjects_taught", type=int, is_dropdown = True, set_choices_on_init = False, **{"width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": OrderedDict(enumerate(range(1, 8), 1))})),
			("age_range_id", SlickGridColumn(id = "age_range_id", type=str, is_dropdown = True, foreign_model = "AgeRange", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("teaching_experience_range_id", SlickGridColumn(id = "teaching_experience_range_id", type=str, is_dropdown = True, foreign_model = "TeachingExperienceRange", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("work_experience_subject_range_id", SlickGridColumn(id = "work_experience_subject_range_id", type=str, is_dropdown = True, foreign_model = "WorkExperienceSubjectRange", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("total_load_range_id", SlickGridColumn(id = "total_load_range_id", type=str, is_dropdown = True, foreign_model = "TotalLoadRange", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("load_on_subject_range_id", SlickGridColumn(id = "load_on_subject_range_id", type=str, is_dropdown = True, foreign_model = "LoadOnSubjectRange", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("education_type_id", SlickGridColumn(id = "education_type_id", type=str, is_dropdown = True, foreign_model = "EducationType", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("category_id", SlickGridColumn(id = "category_id", type=str, is_dropdown = True, foreign_model = "EduCategory", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("retraining_institution_id", SlickGridColumn(id = "retraining_institution_id", type=str, is_dropdown = True, foreign_model = "RetrainingInstitution", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("retraining_date_id", SlickGridColumn(id = "retraining_date_id", type=str, is_dropdown = True, foreign_model = "RetrainingDate", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("training_institution_id", SlickGridColumn(id = "training_institution_id", type=str, is_dropdown = True, foreign_model = "TrainingInstitution", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("training_date_id", SlickGridColumn(id = "training_date_id", type=str, is_dropdown = True, foreign_model = "TrainingDate", **{"minWidth": 200, "formatter": "Select2Formatter",  "editor": "Select2Editor"})),
			("predmet_n1", SlickGridColumn(id = "predmet_n1", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("predmet_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 2)}})),
			("predmet_n2", SlickGridColumn(id = "predmet_n2", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("predmet_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 2)}})),
			("predmet_n3", SlickGridColumn(id = "predmet_n3", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("predmet_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 2)}})),
			("predmet_n4", SlickGridColumn(id = "predmet_n4", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("predmet_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 2)}})),
			("predmet_n5", SlickGridColumn(id = "predmet_n5", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("predmet_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 3)}})),
			("predmet_n6", SlickGridColumn(id = "predmet_n6", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("predmet_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 3)}})),
			("metod_n7", SlickGridColumn(id = "metod_n7", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("metod_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 3)}})),
			("metod_n8", SlickGridColumn(id = "metod_n8", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("metod_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 3)}})),
			("metod_n9", SlickGridColumn(id = "metod_n9", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("metod_competition"), "width": 100, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 3)}})),
			("psy_ped_n10", SlickGridColumn(id = "psy_ped_n10", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("psy_ped_competition"), "width": 450, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 4)}})),
			("communication_n11", SlickGridColumn(id = "communication_n11", type=int, is_dropdown = True, set_choices_on_init = False, **{"columnGroup": lazy_gettext("communication_competition"), "width": 450, "formatter": "Select2Formatter",  "editor": "Select2Editor", "dataSource": {i: str(i) for i in range(0, 4)}})),
		])
		
		self.options = {
			"editable": True,
			"enableAddRow": True,
			"enableColumnReorder": False,
			"enableCellNavigation": True,
			"asyncEditorLoading": False,
			"autoEdit": False,
			"createPreHeaderPanel": True,
			"showPreHeaderPanel": True,
			"preHeaderPanelHeight":23*3,
			"explicitInitialization": True,
			"multiColumnSort": False,
            "rowHeight": 100 # <--- here
		}
		
		super(self.__class__, self).__init__()