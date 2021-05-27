import requests
import json


#* Обязательные заголовки без которых не работает
headers = {
	'Content-type': 'application/json',  # Определение типа данных
	'Accept': 'text/plain',
	'Content-Encoding': 'utf-8'
}

# >>> ngrok http 5000
server_domain = 'http://127.0.0.1:5000'  # 'http://127.0.0.1:5000'


def is_login_unique(login: str) -> bool:
	"""Этот запрос ищет первое совпадение созданной строки `login` с логинами из таблицы <User>.
	Возвращает булевое значение того, является ли `login` уникальным.
	"""
	print('<func> is_login_unique')

	data = {'login': login}
	try:
		r = requests.post(
			url=f'{server_domain}/is-login-unique',
			data=json.dumps(data),
			headers=headers
		)
		print(f'\t"POST {server_domain}/is-login-unique" {r.status_code}')
		print(f"\t{r.text}")

		if 400 > r.status_code > 199:
			print(f'\tTrue\n')
			return True
		else:
			print(f'\tFalse\n')
			return False

	except Exception as e:
		print(e)
		print("\tFalse\n")
		return False


def sign(data: dict) -> bool:
	"""
		{
			'team_name': self.ids.toolbar.title,
			'users': [
				{
					'user_login':    str,
					'user_password': str,
					'user_name':     str,
					'user_role':     str,
				}
			],
			'roles': List[str]
		}
	"""
	print('\n<func> sign')

	try:
		r = requests.post(
			url=f'{server_domain}/register',
			data=json.dumps(data),
			headers=headers
		)

		print(f'\t"POST {server_domain}/register" {r.status_code}')
		print(f"\t{r.text}")

		# Возвращает булевое значение в соответсвие с кодом статуса ответа  
		if 400 > r.status_code > 199:
			print(f'\tTrue\n')
			return True
		else:
			print(f'\tFalse\n')
			return False
		
	except Exception as e:
		print("\tОшибка регистрации\n", f"\t{e}\n")
		print(f'\tFalse\n')
		return False


def log(data: dict) -> bool:
	"""
		{
			'login': str, 
			'password': str
		}
	"""
	print('\n<func> log')

	try:
		r = requests.post(
			url=f'{server_domain}/enter',
			data=json.dumps(data),
			headers=headers
		)

		print(f'\t"POST {server_domain}/enter" {r.status_code}')
		print(f"\t{r.text}")
		
		if r.status_code == requests.codes.ok:
			print(f'\tTrue\n')
			return True
		else:
			print(f'\tFalse\n')
			return False
		
	except Exception as e:
		print(f'\tFalse')
		print("\tОшибка входа\n", f"\t{e}\n")
		return False


#!!!
def push_tasks_info(tasks: list):
	print('\n<func> push_tasks_info')
	"""
		{
			'tasks_data': [
		           {
		               "task_text":        str,
		               "task_users_login": List[str],
		               "task_users":       List[str],
		               "task_deadline":    datetime.datetime(),
		               "task_is_done":     bool
		           }
		       ]
		}
	"""
	try:
		r = requests.post(
			url=f'{server_domain}/push_tasks_info',
			data=json.dumps(tasks),
			headers=headers
		)

		print(f'\t"POST {server_domain}/push_tasks_info" {r.status_code}')
		print(f"\t{r.text}")

	except Exception as e:
		print("\tОшибка в отправке задач\n", f"\t{e}\n")
		return


def get_tasks_info(account_login: str) -> dict:
	"""
		{
			'tasks_data': [
				{
					"task_text":        str
					"task_user_logins": List[str] 
					"task_user_names":  List[str]
					"task_deadline":    datetime.datetime()
					"task_is_done":     bool
				}
			]
		}
	"""
	print('\n<func> get_tasks_info')

	try:
		r = requests.post(
			url=f'{server_domain}/get_tasks_info',
			data=json.dumps({'account_login': account_login}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/get_tasks_info" {r.status_code}')
		tasks: dict = json.loads(r.text)
		print("tasks: ", json.dumps(tasks, indent=4, ensure_ascii=False), "\n")

		return tasks

	except Exception as e:
		print("\tОшибка в получении словаря задач\n", f"\t{e}\n")
		return {}


def get_team_users(account_login: str) -> dict:
	"""Словарь из 2 списков: 1)логины 2)имена
		{
			'user_logins': List[str]
			'user_names':  List[str]
		}
	"""
	print('\n<func> get_team_users')

	try:
		r = requests.post(
			url=f'{server_domain}/get_team_users',
			data=json.dumps({'account_login': account_login}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/get_team_users" {r.status_code}')
		data: dict = json.loads(r.text)
		print("data: ", json.dumps(data, indent=4, ensure_ascii=False), "\n")

		return data

	except Exception as e:
		print("\tОшибка в получении имени команды\n", f"\t{e}\n")
		return {}


def get_team_name(account_login: str) -> str:
	print('\n<func> get_team_name')

	try:
		r = requests.post(
			url=f'{server_domain}/get_team_name',
			data=json.dumps({'account_login': account_login}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/get_team_name" {r.status_code}', "\n")
		return json.loads(r.text)['team_name']

	except Exception as e:
		print("\tОшибка входа\n", f"\t{e}\n")
		return ''

