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
			print(f'\tTrue')
			return True
		else:
			print(f'\tFalse')
			return False

	except Exception as e:
		print(e)
		print("\tFalse")
		return False


def sign(data: dict) -> bool:
	print('<func> sign')

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
			print(f'\tTrue')
			return True
		else:
			print(f'\tFalse')
			return False
		
	except Exception as e:
		print("Ошибка регистрации\n", e)
		print(f'\tFalse')
		return False


def log(data: dict) -> bool:
	print('<func> log')

	r = None
	try:
		r = requests.post(
			url=f'{server_domain}/enter',
			data=json.dumps(data),
			headers=headers
		)

		print(f'\t"POST {server_domain}/enter" {r.status_code}')
		print(f"\t{r.text}")
		
		if r.status_code == requests.codes.ok:
			print(f'\tTrue')
			return True
		else:
			print(f'\tFalse')
			return False
		
	except Exception as e:
		print(f'\tFalse')
		print("Ошибка входа\n",e)
		return False


#!!!
def push_tasks_info(tasks: list):
	print('<func> push_tasks_info')
	"""
		{
			'tasks_data': [
		           {
		               "task_text":f"Сосать бибу {i}",
		               "task_users_login":["huesos1login","huesos2login"],
		               "task_users":["хуесос 1", "Хуесос 2"],
		               "task_deadline":"21 апреля, 2021",
		               "task_is_done":0
		           } for i in range(10)
		       ]
		}
	"""
	
	r = None
	try:
		r = requests.post(
			url=f'{server_domain}/push_tasks_info',
			data=json.dumps(tasks),
			headers=headers
		)

		print(f'\t"POST {server_domain}/push_tasks_info" {r.status_code}')
		print(f"\t{r.text}")

	except Exception as e:
		print("Ошибка в отправке задач\n", e)


def get_tasks_info(account_login: str) -> dict:
	"""
		{
			'tasks_data': [
				{
					"task_text": str()
					"task_user_logins": [str(), ...] 
					"task_user_names": [str(), ...]
					"task_deadline": #! datetime.datetime()
					"task_is_done": bool()
				}
			]
		}
	"""
	print('<func> get_tasks_info')

	try:
		r = requests.post(
			url=f'{server_domain}/get_tasks_info',
			data=json.dumps({'account_login': account_login}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/get_tasks_info" {r.status_code}')
		tasks: dict = json.loads(r.text)
		print("tasks: ", json.dumps(tasks, indent=4, ensure_ascii=False))

		return tasks

	except Exception as e:
		print("Ошибка в получении словаря задач\n", e)
		return {}


def get_team_users(account_login: str) -> dict:
	""" Словарь из 2 списков: 1)логины 2)имена """
	print('<func> get_team_users')

	try:
		r = requests.post(
			url=f'{server_domain}/get_team_users',
			data=json.dumps({'account_login': account_login}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/get_team_users" {r.status_code}')
		data: dict = json.loads(r.text)
		print("data: ", json.dumps(data, indent=4, ensure_ascii=False))

		return data

	except Exception as e:
		print("Ошибка в получении имени команды\n",e)
		return {}


def get_team_name(account_login: str) -> str:
	print('<func> get_team_name')

	try:
		r = requests.post(
			url=f'{server_domain}/get_team_name',
			data=json.dumps({'account_login': account_login}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/get_team_name" {r.status_code}')
		return json.loads(r.text)['team_name']

	except Exception as e:
		print("Ошибка входа\n",e)
		return ''

