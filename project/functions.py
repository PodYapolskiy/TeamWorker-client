import secrets
import string
from functools import partial

from .app import is_login_unique


def generate_string(unique=False) -> str:
	"""
		Генерирует строку. Либо уникальную, либо нет.
	"""

	# Генерирует просто строку
	pickchar = partial(secrets.choice, string.ascii_uppercase + string.digits)
	login = ''.join([pickchar() for _ in range(10)])

	if not unique:  #// (test_block)
		print(f'just string: "{login}"')

	# Путём перебора и обращения к таблице 'Users', узнаём является login уникальным
	if unique:
		while True:
			# Этот запрос ищет первое совпадение созданной строки 'login' с логинами из таблицы <User>
			#* Если login совпадает, конструкция ниже не сработает
			if is_login_unique(login):  #!!!
				print(f'unique login in app.db: "{login}"')
				return login
	
			pickchar = partial(secrets.choice, string.ascii_uppercase + string.digits)
			login = ''.join([pickchar() for _ in range(10)])
	
	return login
