from intro_to_flask import app
from intro_to_flask import models
from intro_to_flask import form_factory

form_factory = form_factory.FormFactory(app)

def main():
	StudentForm = form_factory.create_form(models.Student, "student_form")
	print(StudentForm.template_str)

if __name__ == "__main__":
	main()
