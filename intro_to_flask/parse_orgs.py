# -*- coding: utf-8 -*-
import re
import pandas as pd
import numpy as np
from collections import OrderedDict
from os.path import join, dirname, realpath

server = True

if server:
	if __name__ == "__main__":
		import sys
		sys.path.append(realpath(join(dirname(__file__), "..")))
		#print(sys.path)
	from intro_to_flask import app

	if __name__ == "__main__":
		from models import Organization, Municipality
	else:
		from .models import Organization, Municipality

	import sqlalchemy as sa
	import sqlalchemy.orm as orm
	import sqlalchemy.exc

	engine = sa.create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True,  encoding="utf8")
	session = orm.Session(bind=engine)

else:
	class App:
		def __init__(self):
			pass

	app = App()
	app.config = dict()
	app.config["DATAFRAMES_DIR"] = "c:\\"

u = lambda x: x

pd.options.mode.chained_assignment = None

filtered_columns = {"Наименование образовательной организации": "name",
					"ИНН": "inn",
					"Место нахождения образовательной организации": "address",
					"Муниципальное образование": "municipality",
					"Краткое наименование": "short_name",
					'''Географические координаты  
(широта)''': "latitude",
					'''Географические координаты 
(долгота)''': "longitude",
					"Серия, номер лицензии": "license_num",
					"Статус лицензии": "license_status",
					"Основание и дата прекращения действия лицензии / переоформления лицензии": "license_details"
}

municipality_to_id = OrderedDict([(o.name_of_municipality, o.id) for o in Municipality.query.all()])

_ = lambda x: filtered_columns[x]

def name_parser():
	pre_replace = dict([
	  (u("Южно-Российский лицей казачества и народов Кавказа"), u("Южно-Российский лицей")),
	  (u("\n"), u(" ")),
	  ("образова-тельное", "образовательное"),
	  ("об-щеобразовательная", "общеобразовательная")
	])
	dict_replace = dict([
	  (u("МУНИЦИПАЛЬНОЕ"), u("М")),
	  (u("ФИЛИАЛ"), u("Ф. ")),
	  (u("КАЗЁННОЕ"), u("К")),
	  (u("КАЗЕННОЕ"), u("К")),
	  (u("БЮДЖЕТНОЕ"), u("Б")),
	  (u("ОБЩЕОБРАЗОВАТЕЛЬНОЕ"), u("О")),
	  (u("ОБШЕОБРАЗОВАТЕЛЬНОЕ"), u("О")),
	  (u("ОСНОВНАЯ"), u("О")),
	  (u("ОБЩЕОБРАЗОВАТЕЛЬНАЯ"), u("О")),
	  (u("ОБШЕОБРАЗОВАТЕЛЬНАЯ"), u("О")),
	  (u("СРЕДНЯЯ"), u("С")),
	  (u("НАЧАЛЬНАЯ"), u("Н")),
	  (u("ШКОЛА"), u("Ш")),
	  (u("УЧРЕЖДЕНИЕ"), u("У ")),
	  (u("ОРГАНИЗАЦИЯ"), u("О")),
	])
	
	list_suppress = [
	  u("«"),
	  u("»"),
	  u("\""),
	  u("с углубленным изучением английского языка"),
	  u("с углубленным изучением отдельных предметов"),
	  u("Новопавловская"),
	  u("Свято-Никольская классическая"),
	  u("Свято-Успенская"),
	  u("им. Героя России В. Духина")
	]
	
	def parse_name(name):
		base = ""
		number = ""
		digit_found = False
		for i in name:
			if not i.isdigit():
				if digit_found: break
				base += i
			else:
				digit_found = True
				number += i
		return base, number
		
	def prepare_name(name, pre_replace, dict_replace, list_suppress):
		res = []
		name = re.sub("\s\s+" , " ", name)
		name = name.replace("  ", " ")
		#print(name)
		if len(name) >= 11 and len(name) <= 14:
			name = name.replace(u("№ "), u("№"))
		for k, v in pre_replace.items():
			name = name.replace(k, v)
		for i in list_suppress:
			name = name.replace(i, "")
		tokens = name.split(" ")
		dict_replace_keys = dict_replace.keys()
		for token in tokens:
			token_upper = token.upper()
			if token_upper in dict_replace_keys:
				res.append(dict_replace[token_upper])
			else:
				res.append(token + " ")
				
		return "".join(res)
		
	return pre_replace, dict_replace, list_suppress, parse_name, prepare_name

def short_names(names):
	pre_replace, dict_replace, list_suppress, parse_name, prepare_name = name_parser()

	res = []
	names_glob = []
	for n, name in names.items():
		basename, number = parse_name(name)
		if number and basename.find(u("№")) == -1:
			basename += u("№")
		if number and not number in names_glob:
			names_glob.append(number)
			prepared_name = prepare_name(basename, pre_replace, dict_replace, list_suppress) + number
		else:
			basename = name
			prepared_name = prepare_name(name, pre_replace, dict_replace, list_suppress)

		if prepared_name.count("(") == 1 and prepared_name.count(")") == 1:
			prepared_name = prepared_name.split("(")[-1].split(")")[0]
		res.append((n, prepared_name))
	return dict(res)

addr_replacements = OrderedDict([
			("Георгиевск", "Георгиевский"),
			("Благодарный", "Благодарненский"),
			("Изобильный", "Изобильненский"),
			("Кочубеевское", "Кочубеевский"),
			("Грачевский", "Грачёвский"),
			("Буденновский", "Будённовский"),
			("Минеральные", "Минераловодский"),
			("Советская", "Советский"),
			("Нефтекумск", "Нефтекумский"),
			("Новоалександровск", "Новоалександровский"),
			("Михайловск", "Шпаковский"),
			("Григорополисская", "Новоалександровский"),
			("Буденновск", "Будённовский")
		])

def address_tokenize(address):
	stop_list = ["с.", "ул.", "г.", "город", "район", "Ставропольский край "]
	for i in stop_list:
		address = address.replace(i, "")

	for k, v in addr_replacements.items():
		if not v in address:
			address = address.replace(k, v)

	return [t for t in re.split(" |,|\n|\xa0", address) if t]

def address_to_mo(address):
	tokens = address_tokenize(address)

	allowed = [i.upper() for i in ['Новоалександровский', 'Андроповский', 'Апанасенковский', 'Арзгирский', 'Благодарненский', 'Будённовский', 'Георгиевский', 'Грачёвский', 'Изобильненский', 'Ипатовский', 'Кировский', 'Кочубеевский', 'Красногвардейский', 'Курский', 'Левокумский', 'Минераловодский', 'Нефтекумский', 'Новоселицкий', 'Александровский', 'Петровский', 'Предгорный', 'Советский', 'Степновский', 'Труновский', 'Туркменский', 'Шпаковский', 'Ессентуки', 'Железноводск', 'Кисловодск', 'Лермонтов', 'Невинномысск', 'Пятигорск', 'Ставрополь']]

	mo = "not found"
	for t in tokens:
		if t.upper() in allowed:
			return t

	return mo

def main():
	df = pd.read_excel(join(app.config["DATAFRAMES_DIR"],
		"Общеобразовательные организации  (апрель_2019).xlsx"), sheet_name = 'Лист3', skiprows = [1])

	#df.ИНН = df.ИНН.astype(int)

	data_dict = df.to_dict()
	addr = data_dict["Место нахождения образовательной организации"]

	mo_list = []

	tmp_mo = []
	for a in addr.values():
		mo = address_to_mo(a)
		tmp_mo.append(mo)
		if not mo in mo_list:
			mo_list.append(mo)

	#print(mo_list)

	data_dict["Муниципальное образование"] = dict(enumerate(tmp_mo))
	data_dict["Краткое наименование"] = dict()
	df = pd.DataFrame.from_dict(data_dict)
	for mo in mo_list:
		org_full_names = df.loc[df["Муниципальное образование"] == mo].to_dict()["Наименование образовательной организации"]
		names = short_names(org_full_names)
		#data_dict = df.to_dict()
		for n, name in names.items():
			data_dict["Краткое наименование"][n] = name

	new_dict = dict()
	for column, column_new in filtered_columns.items():
		new_dict[column_new] = data_dict[column]
	df = pd.DataFrame.from_dict(new_dict)

	filtered_df = filter_orgs(df)
	filtered_df.to_excel(join(app.config["DATAFRAMES_DIR"], "orgs_new.xlsx"))
	return
	#filtered_df.to_csv(join(app.config["DATAFRAMES_DIR"], "mytest2.csv"))
	for n in municipality_to_id.values():
		print(n)
		tmp_df = filtered_df.loc[filtered_df["municipality_id"] == n]
		try:
			session.bulk_insert_mappings(Organization, tmp_df.to_dict(orient="records"))
		except sqlalchemy.exc.InvalidRequestError as e:
			session.rollback()
			session.close()
			print("municipality_id = %d" % n)
			print(str(e))
			return df

	session.commit()
	session.close()
	#filtered_df.to_excel(join(app.config["DATAFRAMES_DIR"], "mytest5.xlsx"))
	#return filtered_df
	return df

def get_inn_by_mo_orgs(df, mo, names):
	tmp_dict = dict()
	for i in names:
		#entry = df.loc[df["Муниципальное образование"] == mo].loc[df["Наименование образовательной организации"] == i]["ИНН"]
		entries = df.loc[df[_("Муниципальное образование")] == mo]
		f_names = entries.to_dict()[_("Наименование образовательной организации")].values()
		f_inn = entries.to_dict()[_("ИНН")].values()
		for name, inn in zip(f_names, f_inn):
			tmp_dict[name.upper()] = inn

		if not i.upper() in tmp_dict:
			print("not found: (%s, %s)" % (mo, i))
			print(tmp_dict)
		else:
			yield int(tmp_dict[i.upper()])

		#if entry.empty:
		#	print("not found: (%s, %s)" % (mo, i))
		#else:
		#	print(int(list(entry.to_dict().values())[0]))

def get_inns_from_excel(df):
	df_mo = pd.read_excel(join(app.config["DATAFRAMES_DIR"], "Разбита по муниципалам.xlsx"), sheet_name = 'Лист1')
	inns = []
	for tmp_d in df_mo.to_dict().items():
		mo = tmp_d[0]
		#if mo != "Ставрополь":
		#	continue
		orgs = [i for i in tmp_d[1].values() if str(i)!= "nan"]
		inns += list(get_inn_by_mo_orgs(df, mo, orgs))

	return inns

def get_inns_from_txt():
	inns_txt = join(app.config["DATAFRAMES_DIR"], "inns.txt")
	return [int(i) for i in open(inns_txt, "r").read().split("\n") if i]

def filter_orgs(df):
	inns = get_inns_from_txt()
	#inns = get_inns_from_excel(df)
	df_res = df.loc[df[_("ИНН")].isin(inns)]
	df_res.sort_values(_("Муниципальное образование"), inplace = True)
	df_res.drop_duplicates(subset = _("ИНН"), keep = "last", inplace = True)

	data_dict = df_res.to_dict()
	new_dict = dict()
	for column, column_new in filtered_columns.items():
		if column_new == _("Муниципальное образование"):
			#print("not found" in data_dict[column_new].values())
			#print([k for (k, v) in data_dict[column_new].items() if v == "not found"])
			ids_not_found = [k for (k, v) in data_dict[column_new].items() if v == "not found"]
			for id in ids_not_found:
				i = df_res.index.get_loc(id)
				print(df_res.iloc[i].to_dict()["address"].replace("\n", " "))
				print(df_res.iloc[i].to_dict()[_("Муниципальное образование")])
				#print(df_res.iloc[id,:].to_dict().items())
		new_dict[column_new] = data_dict[column_new]

	#return df_res

	munitipality_dict = data_dict[_("Муниципальное образование")]
	#for k, v in munitipality_dict.items():
	#	munitipality_dict[k] = municipality_to_id[v]

	#new_dict["municipality_id"] = munitipality_dict
	#del new_dict["municipality"]

	inn_dict = new_dict[_("ИНН")]
	for k, v in inn_dict.items():
		inn_dict[k] = int(v)

	new_dict[_("ИНН")] = inn_dict

	df_res = pd.DataFrame.from_dict(new_dict).replace(np.nan, '', regex=True)
	return df_res


if __name__ == "__main__":
	df = main()
