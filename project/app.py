import requests
import json

from typing import Tuple

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


def get_tasks_info(account_login: str) -> Tuple[list, bool]:
	"""Возвращает список задач в таком формате:\n
		[
			{
				"task_id":          int
				"task_text":        str
				"task_user_logins": List[str] 
				"task_user_names":  List[str]
				"task_deadline":    datetime.datetime()
				"task_is_done":     bool
			}
		]
	"""
	print('\n<func> get_tasks_info')

	try:
		r = requests.post(
			url=f'{server_domain}/get_tasks_info',
			data=json.dumps({'account_login': account_login}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/get_tasks_info" {r.status_code}')
		tasks: list = json.loads(r.text)
		print("tasks:\n", json.dumps(tasks, indent=4, ensure_ascii=False), "\n")

		return tasks, True

	except Exception as e:
		print("\tОшибка в получении словаря задач\n", f"\t{e}\n")
		return [], False


def get_team_users(account_login: str) -> dict:
	"""Словарь из 2 списков: 1)логины 2)имена\n
		{
			'user_logins': List[str]
			'user_names':  List[str]
			'user_roles':  List[str]
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
		print("\tОшибка в получении доп инфы о пользователях команды\n", f"\t{e}\n")
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


def push_task_info(task: dict) -> bool:
	"""Отправляет задачу на сервер в таком виде:\n
		{
			"task_text":        str,
			"task_users_login": List[str],
			"task_deadline":    str,
			"task_is_done":     bool
		}
	"""
	print('\n<func> push_tasks_info')

	try:
		r = requests.post(
			url=f'{server_domain}/push_task_info',
			data=json.dumps(task),
			headers=headers
		)

		print(f'\t"POST {server_domain}/push_task_info" {r.status_code}')
		print(f"\t{r.text}")

		if 400 > r.status_code > 199:
			print(f'\tTrue\n')
			return True
		else:
			print(f'\tFalse\n')
			return False

	except Exception as e:
		print("\tОшибка в добавлении задачи\n", f"\t{e}\n")
		return False


def change_task_state(id: int) -> bool:
	"""Функция должна изменять состояние задачи по её `id`. Это оптимизирует работу приложения.
		Возвращает булевое значение того, насколько удачно прошло изменение.
	"""
	print('\n<func> change_task_state')
	
	try:
		r = requests.post(
			url=f'{server_domain}/change_task_state',
			data=json.dumps({"task_id": id}),
			headers=headers
		)

		print(f'\t"POST {server_domain}/change_task_state" {r.status_code}')
		print(f"\t{r.text}")

		if 400 > r.status_code > 199:
			print(f'\tTrue\n')
			return True
		else:
			print(f'\tFalse\n')
			return False

	except Exception as e:
		print("\tОшибка в изменении статуса задачи\n", f"\t{e}\n")
		return False
