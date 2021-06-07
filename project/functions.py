import secrets
import string
from functools import partial

from .app import is_login_unique


def generate_string(unique=False) -> str:
	"""Генерирует строку. Либо уникальную, либо нет."""

	# Генерирует просто строку
	pickchar = partial(secrets.choice, string.ascii_uppercase + string.digits)
	login = ''.join([pickchar() for _ in range(10)])

	# Путём перебора и обращения к таблице 'Users', узнаём является login уникальным.
	if unique:
		while True:
			# Если login совпадает, конструкция ниже не сработает
			if is_login_unique(login):
				return login
	
			pickchar = partial(secrets.choice, string.ascii_uppercase + string.digits)
			login = ''.join([pickchar() for _ in range(10)])
	
	return login


def convert_month(month: str) -> str:
	"""Функция, переводящая значение `month` в строку с численным значением.\n
		Пример:\n
			convert_month('Apr') -> '04'
	"""
	monthes = {
		'Jan': '01',
		'Feb': '02',
		'Mar': '03',
		'Apr': '04',
		'May': '05',
		'Jun': '06',
		'Jul': '07',
		'Aug': '08',
		'Sep': '09',
		'Oct': '10',
		'Nov': '11',
		'Dec': '12',
	}
	return monthes[month]

