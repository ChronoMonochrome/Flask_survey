from wtforms.validators import Required, Length, EqualTo
from wtforms import Field
from wtforms.widgets import html_params
from flask import Markup

# https://stackoverflow.com/questions/14510630/wtforms-creating-a-custom-widget
class InlineButtonWidget(object):
	html_params = staticmethod(html_params)

	def __init__(self, input_type='submit', text=''):
		self.input_type = input_type
		self.text = text

	def __call__(self, field, **kwargs):
		kwargs.setdefault('id', field.id)
		kwargs.setdefault('type', self.input_type)
		if 'value' not in kwargs:
			kwargs['value'] = field._value()
		return Markup('<button %s><span>%s</span></button>' % (self.html_params(name=field.name, **kwargs), field.text))


class InlineButton(Field):
	widget = InlineButtonWidget()

	def __init__(self, label=None, validators=None, text='Save', **kwargs):
		super(InlineButton, self).__init__(label, validators, **kwargs)
		self.text = text

	def _value(self):
		if self.data:
			return u''.join(self.data)
		else:
			return u''

class BootstrapSliderWidget(object):
	html_params = staticmethod(html_params)

	def __init__(self, def_min = 0, def_max = 10, def_step = .01):
		self.def_min = def_min
		self.def_max = def_max
		self.def_step = def_step
		self.defaults = {"data-slider-min": self.def_min,
				     "data-slider-max": self.def_max,
				     "data-slider-step": str(self.def_step),
				     "data-slider-ticks": "[{min}, {max}]".format(min = self.def_min, max = self.def_max),
				     "data-slider-ticks-snap-bounds": "1",
				     "data-slider-ticks-labels": "['{min}', '{max}']".format(min = self.def_min, max = self.def_max)
				}

	def __call__(self, field, **kwargs):
		kwargs.setdefault('id', field.id)
		for key, val in self.defaults.items():
			kwargs.setdefault(key, self.defaults.get(key, val))

		if 'value' not in kwargs:
			kwargs['value'] = field._value()

		#print(kwargs)

		return Markup("""<input {params} />\n""".format(
				    params = self.html_params(name=field.name, **kwargs)
			      ))

class BootstrapSlider(Field):
	def __init__(self, label, validators = None, def_min = 0, def_max = 10, def_step = .01, **kwargs):
		self.widget = BootstrapSliderWidget(def_min, def_max, def_step)
		super(self.__class__, self).__init__(label, validators, widget = self.widget, **kwargs)

class DatePicker(Field):
	def __init__(self, label, validators = None, language = "en", **kwargs):
		self.widget = DatePickerWidget(language)
		super(self.__class__, self).__init__(label, validators, widget = self.widget, **kwargs)

class DatePickerWidget(object):
	html_params = staticmethod(html_params)

	def __init__(self, language):
		self.language = language
		self.defaults = {"language": self.language}

	def __call__(self, field, **kwargs):
		kwargs.setdefault('id', field.id)
		for key, val in self.defaults.items():
			kwargs.setdefault(key, self.defaults.get(key, val))

		if 'value' not in kwargs:
			kwargs['value'] = field._value()

		#print(kwargs)

		return Markup("""<input {params} type="text" />""".format(params = self.html_params(name=field.name, **kwargs)))
		
class SlickGridWidget(object):
	html_params = staticmethod(html_params)

	def __init__(self, style):
		self.style = style

	def __call__(self, field, **kwargs):
		kwargs.setdefault('id', field.id)
		style_str = ""
		#print(self.style)
		for k, v in self.style.items():
			style_str += "{k}: {v};".format(k = k, v = v)

		kwargs.setdefault('style', style_str)
		if 'value' not in kwargs:
			kwargs['value'] = field._value()
		return Markup('<div %s></div>' % (self.html_params(name=field.name, **kwargs)))


class SlickGrid(Field):
	def __init__(self, label=None, validators=None, style={"width": "100%", "height": "500px"}, **kwargs):
		self.widget = SlickGridWidget(style)
		super(SlickGrid, self).__init__(label, validators, widget = self.widget, **kwargs)

	def _value(self):
		if self.data:
			return u''.join(self.data)
		else:
			return u''
