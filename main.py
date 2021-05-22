import kivy
kivy.require('2.0.0')

# Импорт из kivy
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.clipboard import Clipboard

# Импорт из kivymd
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.picker import MDTimePicker, MDDatePicker
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import Snackbar

# Импорт своих модулей из пакета project
from project import sign, log, push_tasks_info, get_tasks_info, get_team_name, get_team_users, generate_string

# Импорт других модулей
import json
from datetime import datetime

#// (test)
from kivy.core.window import Window  # - для понимания с компьютера, убирать перед компиляцией
Window.size = (480, 840)

Config.set('kivy', 'keyboard_mode', 'systemanddock')  # открытие клавиатуры при нажатиях с телефона

delete_if_exit = True
roles = []
val1, val2, val3 = False, False, False

'''
class Singleton(type):
	"""Метакласс. Паттерн проектирования 'одиночка'."""
	# def __init__(cls, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	_instance = None
	
	def __call__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super().__call__(*args, **kwargs)
		return cls._instance


class Logger(metaclass=Singleton):
	"""Действующий авторизованный профиль."""
	login = None  # Логин авторизованного пользователя
	team_name = None  # Название команды #! Чтобы не обращаться каждый раз к серверу.

	def set_login(self):
		pass

	def set_team(self):
		pass


account = Logger()  # Авторизованный аккаунт на клиенте. По умолчанию None
'''

# Переменная, указывающая на login пользователя, данной, конкретной сессии
account_login = None


class StartScreen(Screen):
	"""Начальный экран"""
	def define_screens(self):
		"""Создаёт ссылки на экраны"""
		global registration_screen_link
		global sign_in_screen_link
		global role_edit_screen_link
		global main_screen_link
		global task_screen_link
		global task_members_screen_link

		registration_screen_link = self.manager.get_screen('registration_screen')
		sign_in_screen_link = self.manager.get_screen('sign_in_screen')
		role_edit_screen_link = self.manager.get_screen('role_edit_screen')
		main_screen_link = self.manager.get_screen('main_screen')
		task_screen_link = self.manager.get_screen('task_screen')
		task_members_screen_link = self.manager.get_screen('task_members_screen')


class SignInScreen(Screen):
	"""Экран регистрации"""
	dialog = None

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.create_user_box()
		self.ids.container.children[user_box_id].text = "<Введите Ваше имя>"
		self.ids.container.children[user_box_id].secondary_text = "Капитан"

	class SwipeToDeleteItem(MDCardSwipe, Screen):
		"""Класс карточки с пользователем"""
		text = StringProperty()
		secondary_text = StringProperty()

		def change_screen(self, instance):  # функция, меняющая тексты на экране регистрации пользователя
			print("<method> change_screen")
			global user_box_id
			global delete_if_exit
			global registration_screen_link
			self.set_user_box_id(instance)
			registration_screen_link.ids.name.text = instance.text
			registration_screen_link.ids.role.text = instance.secondary_text
			registration_screen_link.ids.label.text = "Изменить данные пользоватея"
			registration_screen_link.ids.button.text = "[color=#ffffff][b]СОХРАНИТЬ ДАННЫЕ[/b][/color]"
			registration_screen_link.ids.warning_label.text = ""
			screen_manager.current = "registration_screen"
			screen_manager.transition.direction = 'left'
			delete_if_exit = False # переменная, отвечающая за то, будет ли по нажатию кнопки обратно в меню регистрации удалятся созданная заранее карточка

		def set_user_box_id(self, instance):  # Функция, определяющая айдишник карточки
			print("<method> set_user_box_id")
			global user_box_id
			global sign_in_screen_link
			user_box_id = sign_in_screen_link.ids.container.children.index(instance)

		def remove_card(self, instance):
			global sign_in_screen_link
			print('udaleniye')
			sign_in_screen_link.ids.container.remove_widget(instance)

	class EditTeamName(BoxLayout):
		""" Текстовое поле диалогового окна """
		team_name = ObjectProperty()

	@staticmethod
	def back_to_start():
		print('<staticmethod> back_to_start')
		screen_manager.transition.direction = 'up'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'start_screen'
	
	def sign_in(self):
		"""  Регистрация новой команды  """
		print("<method> sign_in")

		global data
		global roles
		global account_login

		for role in roles:
			print(f"\t{role}")

		# Данные, которые будут отправлены на сервер
		data = {
			'team_name': self.ids.toolbar.title,
			'users': [],
			'roles': []
		}

		exist_roles = []  # Костыль (очередной). Нужен, чтобы на сервер не отправлялись неиспользованные созданные роли

		# Пробегаемся по всех созданным пользователям
		for i in range(len(self.ids.container.children)):
			user_dict = {}  # Временный словарь для каждой итерации

			# Генерируем значения логина и пароля пользователя
			user_login = generate_string(unique=False)  #!!!
			user_dict['user_login'] = user_login
			user_dict['user_password'] = generate_string(unique=False)

			# Задаём во временный словарь параметры пользователя
			user_role = self.ids.container.children[i].secondary_text
			user_dict['user_name'] = self.ids.container.children[i].text
			user_dict['user_role'] = user_role

			exist_roles.append(user_role)
			data['users'].append(user_dict)  # Добавление словаря пользователя в список пользователей 

			# Основным аккаунтом данной сессии является аккаунт с этим логином
			if user_role == "Капитан":
				account_login = user_login

		# удаляет из ролей те, которые не были использованы на момент нажатия кнопки регистрации
		for role in roles.copy():
			if role['role_name'] not in exist_roles:
				roles.remove(role)

		data['roles'] = roles

		print(json.dumps(data, indent=4, ensure_ascii=False))

		if sign(data):
			self.manager.transition.direction = 'down'
			self.manager.transition.duration = 0.5
			self.manager.current = 'info_screen'
		else:
			Snackbar(text="Не удалось передать данные на сервер", font_size="18dp").open()

			if test:
				self.manager.transition.direction = 'down'
				self.manager.transition.duration = 0.5
				self.manager.current = 'info_screen'

	def edit_team_name(self):
		""" Создаёт диалоговое окно """
		print("<method> edit_team_name")

		if not self.dialog:
			self.dialog = MDDialog(
				title="Команда",
				type='custom',
				content_cls=self.EditTeamName(),
				radius=[20, 20, 20, 20],
				buttons=[
					MDFlatButton(
						text="ОТМЕНА", 
						text_color=MyApp().theme_cls.primary_color,
						on_release=self.dialog_cancel
					),
					MDRaisedButton(
						text="ПРИНЯТЬ", 
						#text_color=MyApp().theme_cls.primary_color,
						on_release=self.dialog_accept
					),
				],
			)
			self.dialog.size_hint = 0.5, 1.0

		self.dialog.open()
	
	def dialog_cancel(self, instance):
		print("<method> dialog_cancel")
		self.dialog.dismiss()
	
	def dialog_accept(self, instance):
		print("<method> dialog_accept")
		for obj in self.dialog.content_cls.children:
			if isinstance(obj, MDTextField):
				print(obj.text)
				self.ids.toolbar.title = obj.text
		self.dialog.dismiss()

	def clear_fields(self):
		"""Функция, меняющая все тексты в меню регистрации"""
		print("<method> clear_fields")
		registration_screen_link = self.manager.get_screen('registration_screen')
		registration_screen_link.ids.name.text = ""
		registration_screen_link.ids.role.text = "Роль"
		registration_screen_link.ids.label.text = "Регистрация пользователя"
		registration_screen_link.ids.button.text = "[color=#ffffff][b]ЗАРЕГИСТРИРОВАТЬ\nПОЛЬЗОВАТЕЛЯ[/b][/color]"

		registration_screen_link.ids.warning_label.text = ""  # Текст таблички, с сообщением об отсутствии текста в полях

	def create_user_box(self):
		print("<method> create_user_box")
		global user_box_id
		global delete_if_exit

		user_box = self.SwipeToDeleteItem()
		self.ids.container.add_widget(user_box)
		user_box_id = 0
		delete_if_exit = True


class LogInScreen(Screen):
	"""Экран входa"""
	login = ObjectProperty()
	password = ObjectProperty()

	def log_in(self):
		print("<method> log_in")
		global account_login

		login = self.login.text
		password = self.password.text

		data = {'login': login, 'password': password}

		#// В kivy файле для теста
		if log(data):
			account_login = login
			self.manager.transition.direction = 'down'
			self.manager.transition.duration = 0.5
			self.manager.current = 'main_screen'
		else:
			Snackbar(text="Ошибка входа", font_size="18dp").open()
			
			if test:
				self.manager.transition.direction = 'down'
				self.manager.transition.duration = 0.5
				self.manager.current = 'main_screen'


class RegistrationScreen(Screen):  # Экран регистрации пользователя

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		global menu_items
		menu_items = [
			{
				"text": "Капитан",
				"viewclass": "OneLineListItem",
				"on_release": lambda text="Капитан": self.on_menu_action(text)
			},
			{
				"text": "Создать роль",
				"viewclass": "OneLineListItem",
				"on_release": lambda text="Создать роль": self.on_menu_action(text)
			}
		]
		self.menu = MDDropdownMenu(
			caller=self.ids.role,
			items=menu_items,
			position="bottom",
			width_mult=4,
		)

	def on_menu_action(self, item_text):
		print(f'<method> on_menu_action with text: {item_text}')

		global role_edit_screen_link
		global roles  # Чтобы автоматически выдавать все возможности капитану

		if item_text == "Создать роль":
			self.menu.dismiss()
			self.manager.transition.direction ='left'
			self.manager.transition.duration = 0.5
			self.manager.current = 'role_edit_screen'
			role_edit_screen_link.ids.warning_label.text = ""
		else:
			self.ids.role.text = item_text
			self.menu.dismiss()

	def registrate(self):
		print("<method> registrate")
		global user_box_id
		
		sign_in_screen_link = self.manager.get_screen('sign_in_screen')
		# Проверка на наличие текста в полях
		if self.ids.name.text == "" or self.ids.role.text == "Роль":
			self.ids.warning_label.text = "Заполните все поля"
		else:
			sign_in_screen_link.ids.container.children[user_box_id].text = self.ids.name.text
			sign_in_screen_link.ids.container.children[user_box_id].secondary_text = self.ids.role.text
			self.manager.transition.direction ='right'
			self.manager.transition.duration = 0.5
			self.manager.current = 'sign_in_screen'

	def delete_box(self):
		global delete_if_exit
		if delete_if_exit == True:
			print("deleting")
			sign_in_screen_link = self.manager.get_screen('sign_in_screen')
			sign_in_screen_link.ids.container.remove_widget(sign_in_screen_link.ids.container.children[0])


class MainScreen(Screen):
	"""Главный экран"""
	class TaskCard(MDCardSwipe, Screen):
		"""Класс карточки с заданием"""
		text = StringProperty()
		secondary_text = StringProperty()
		tertiary_text = StringProperty()
		active = BooleanProperty()

		class RightCheckbox(IRightBodyTouch, MDCheckbox):
			pass

		def change_screen(self, instance):
			""" Функция, меняющая тексты на экране регистрации пользователя """
			print("<method> change_screen")

			global task_box_id
			global task_screen_link
			global tasks
			global task_box_id

			self.set_task_box_id(instance)
			task_screen_link.ids.text.text = tasks[task_box_id]["task_text"]
			date_and_time = str(tasks[task_box_id]["task_deadline"]).split(" ")
			date = str(date_and_time[0]).split("-")
			time = str(date_and_time[1]).split(":")
			task_screen_link.ids.time_label.text = f'{time[0]}:{time[1]}'
			task_screen_link.ids.date_label.text = f'{date[0]}.{date[1]}.{date[2]}'
			screen_manager.current = "task_screen"
			screen_manager.transition.direction = 'left'

		def set_task_box_id(self, instance):
			""" Функция, определяющая айдишник карточки """
			print("<method> set_user_box_id")

			global task_box_id
			global main_screen_link

			children = main_screen_link.ids.container.children
			task_box_id = len(children) - 1 - children.index(instance)
			print(task_box_id)

		def remove_card(self, instance):
			global main_screen_link
			global tasks
			global account_login
			global task_box_id

			print('<method> remove_card')
			self.set_task_box_id(instance)
			tasks.pop(task_box_id)
			push_tasks_info(tasks)
			main_screen_link.ids.container.remove_widget(instance)

		def on_checkbox_active(self, checkbox, value, instance):
			print("<method> on_checkbox_active")

			global task_box_id
			global tasks
			global account_login

			self.set_task_box_id(instance)
			print({value})
			if value:
				tasks[task_box_id]['task_is_done'] = 1
				print("On")
			else:
				tasks[task_box_id]['task_is_done'] = 0
				print("Off")
			push_tasks_info(tasks)

	def on_enter(self):
		print("<method> on_enter")
		global account_login

		# Тот пользователь, который входит (глобальная переменная)
		# Если вход происходит сразу с SignInScreen, то пользователь - капитан
		# Если с LogInScreen, то тот, который вошёл

		global tasks
		#tasks = [
		#	{
		#		"task_text":f"Сосать бибу {i}",
		#		"task_users_login":["huesos1login","huesos2login"],
		#		"task_users":["хуесос 1", "Хуесос 2"],
		#		"task_deadline":"21 апреля, 2021",
		#		"task_is_done":0
		#	}  for i in range(10)
		#]
		self.ids.toolbar.title = get_team_name(account_login)
		tasks = get_tasks_info(account_login)

		self.ids.container.clear_widgets()
		self.display_tasks()

	def display_tasks(self):
		""" Обновляет список задач """
		print ("<method> display_tasks")
		global tasks

		for task in tasks:
			users = ""
			mark = ", "
			itter = 1

			for user in task["task_users"]:
				if itter >= len(task["task_users"]):
					mark = ""

				itter += 1
				users += user + mark

			self.ids.container.add_widget(
				self.TaskCard(
						text=task["task_text"],
						secondary_text=users,
						tertiary_text=str(task["task_deadline"]),
						active=bool(task["task_is_done"])
				)
			)

	def change_box_id(self):
		global task_box_id
		task_box_id = len(self.ids.container.children)

	@staticmethod
	def back_to_start():
		print('<staticmethod> back_to_start')
		screen_manager.transition.direction = 'up'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'start_screen'
		
	@staticmethod
	def clear_screen():
		task_screen_link.ids.text.text = ""
		task_screen_link.ids.time_label.text = "HH.MM"
		task_screen_link.ids.date_label.text = "YYYY.DD.MM"


class TaskScreen(Screen):
	
	def make_task(self):
		print("<method> make_task")
		global tasks
		global task_box_id

		if self.ids.text.text == "" or self.ids.time_label.text == "HH.MM" or self.ids.date_label.text == "YYYY.DD.MM":
			self.ids.warning_label.text = "Введите все данные"

		else:
			time_list = str(self.ids.time_label.text).split(':')
			date_list = str(self.ids.date_label.text).split('.')
			task = {
				"task_text": str(self.ids.text.text),
				"task_users_login": ["user1_login", "user2_login"],  #!!!
				"task_users": ["Пользователь 1", "Пользователь 2"],  #!!!
				"task_deadline": datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), int(time_list[0]), int(time_list[1])),
				"task_is_done": 0
			}

			# get_team_users(account_login)
			# {
			# 	"users_logins": []
			# 	"users_names": []
			# }

		if len(tasks) != task_box_id:
			tasks.pop(task_box_id)

		tasks.insert(task_box_id, task)
		print(tasks)

		push_tasks_info(tasks)

		self.ids.warning_label.text = ""
		screen_manager.transition.direction = 'right'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'main_screen'

	def show_time_picker(self):
		""" Открытие диалогого окна времени """
		print("<method> show_time_picker")

		time_dialog = MDTimePicker()
		time_dialog.bind(on_save=self.on_save_time)
		time_dialog.open()

	def on_save_time(self, instance, value):
		print("<method> on_save_time")

		time_temp_list = str(value).split(":")
		self.ids.time_label.text = f'{time_temp_list[0]}:{time_temp_list[1]}'
		print(instance, value)

	def show_date_picker(self):
		""" Открытие диалогого окна даты """
		print("<method> show_date_picker")

		date_dialog = MDDatePicker()
		date_dialog.bind(on_save=self.on_save_date)
		date_dialog.open()

	def on_save_date(self, instance, value, date_range):
		print("<method> on_save_date")

		date_temp_list = str(value).split("-")
		self.ids.date_label.text = f'{date_temp_list[0]}.{date_temp_list[1]}.{date_temp_list[2]}'
		print(instance, value, date_range)


class RoleEditScreen(Screen):

	def on_checkbox1_active(self, checkbox, value):
		print("Create_tasks: ", value)
		global val1

		if value:
			val1 = True
		else:
			val1 = False

	def on_checkbox2_active(self, checkbox, value):
		print("Join_tasks: ", value)
		global val2

		if value:
			val2 = True
		else:
			val2 = False

	def on_checkbox3_active(self, checkbox, value):
		print("Inviting: ", value)
		global val3
		
		if value:
			val3 = True
		else:
			val3 = False

	def create_role(self):
		print("<method> create_role")

		global val1
		global val2
		global val3
		global registration_screen_link
		global roles
		global menu_items

		if self.ids.role_name.text != "":
			role = {
				"role_name" : self.ids.role_name.text,
				"create_tasks" : int(val1),
				"join_tasks" : int(val2),
				"inviting" : int(val3)
			}
			roles.append(role)
			item = {
				"text": self.ids.role_name.text,
				"viewclass": "OneLineListItem",
				"on_release": lambda text=f"{self.ids.role_name.text}": registration_screen_link.on_menu_action(text)
			}
			menu_items.insert(len(menu_items)-1, item)

			registration_screen_link.menu = MDDropdownMenu(
				caller=registration_screen_link.ids.role,
				items=menu_items,
				position="bottom",
				width_mult=4,
			)

			registration_screen_link.ids.role.text = self.ids.role_name.text
			self.manager.transition.direction ='right'
			self.manager.transition.duration = 0.5
			self.manager.current = 'registration_screen'
		else:
			self.ids.warning_label.text = "Введите название роли"


class InfoScreen(Screen):

	def on_enter(self):
		global data

		for item in self.ids.info_list.children:
			self.ids.info_list.remove_widget(item)

		for i in range(len(data['users'])):
			user = data['users'][len(data['users'])-1-i]
			self.ids.info_list.add_widget(
				self.UserInfoBox(
						name=user['user_name'],
						role=user['user_role'],
						login=user['user_login'],
						password=user['user_password']
					)
				)

	class UserInfoBox(BoxLayout,RectangularElevationBehavior):
		name = ObjectProperty()
		role = ObjectProperty()
		login = ObjectProperty()
		password = ObjectProperty()
		
		def __init__(self, name, role, login, password, **kwargs):
			super().__init__(**kwargs)
			self.name.text = f'Имя:{name}'
			self.role.text = f'Роль:{role}'
			self.login.text = f'Логин:{login}'
			self.password.text = f'Пароль:{password}'

		def copy_to_clipboard(self, instance):
			Clipboard.copy(f"{instance.login.text}\n{instance.password.text}")


class TaskMembersScreen(Screen):

	class UserCard(MDCardSwipe, Screen):
		""" Класс карточки с пользователем ( и в будующем возможно задания ) """
		text = StringProperty()
		active = BooleanProperty()

		class RightCheckbox(IRightBodyTouch, MDCheckbox):
			pass

		def set_task_box_id(self, instance):
			""" Функция, определяющая айдишник карточки """
			print("<method> set_user_box_id")

			global task_member_box_id
			global task_members_screen_link

			children = task_members_screen_link.ids.container.children
			task_member_box_id = len(children) - 1 - children.index(instance)
			print(task_member_box_id)

		def on_checkbox_active(self, checkbox, value, instance):
			global task_member_box_id
			global tasks
			global account_login
			global team_users

			self.set_task_box_id(instance)
			print({value})

			if value:
				tasks[task_member_box_id]["task_users_login"].append(team_users["users_logins"][task_member_box_id])
				tasks[task_member_box_id]["task_users"].append(team_users["users_names"][task_member_box_id])
				print("On")
			else:
				tasks[task_member_box_id]["task_users_login"].pop([tasks.index(team_users["users_logins"][task_member_box_id])])
				tasks[task_member_box_id]["task_users"].pop([tasks.index(team_users["users_names"][task_member_box_id])])
				print("Off")

			push_tasks_info(tasks)

	def on_enter(self):
		global team_users
		global task_box_id
		global tasks

		self.ids.container.clear_widgets()
		team_users = get_team_users(account_login)
		for user in team_users["users_names"]:
			if user in tasks[task_box_id]["task_users"]:
				user_in_task = True
			else:
				user_in_task = False
			self.ids.container.add_widget(
				self.UserCard(
						text=user,
						active=bool(user_in_task)
					)
				)

	def accept_changes(self):
		pass

	@staticmethod
	def back_to_start():
		print('<staticmethod> back_to_start')
		screen_manager.transition.direction = 'up'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'start_screen'


Builder.load_file("KV.kv")


class MyApp(MDApp):

	def build(self):
		self.theme_cls.primary_palette = 'Teal'  # Основной цвет - бирюзовый
		self.theme_cls.primary_hue = 'A700'  # Оттенок
		self.theme_cls.theme_style = 'Light'  # Светлая тема

		# Управление экранами
		global screen_manager  # Переменная становиться доступна везде
		screen_manager = ScreenManager()
		screen_manager.add_widget(StartScreen(name="start_screen"))
		screen_manager.add_widget(SignInScreen(name="sign_in_screen"))
		screen_manager.add_widget(LogInScreen(name="log_in_screen"))
		screen_manager.add_widget(RegistrationScreen(name="registration_screen"))
		screen_manager.add_widget(MainScreen(name="main_screen"))
		screen_manager.add_widget(TaskScreen(name="task_screen"))
		screen_manager.add_widget(RoleEditScreen(name="role_edit_screen"))
		screen_manager.add_widget(InfoScreen(name="info_screen"))
		screen_manager.add_widget(TaskMembersScreen(name="task_members_screen"))

		return screen_manager

	title = 'TeamWorker alpha 0.1'
	screen = None
	x = 0
	y = 15

	def refresh_callback(self, *args):
		""" Обновляет состояние приложения, пока спиннер остаётся на экране """

		def refresh_callback(interval):
			global main_screen_link
			main_screen_link.ids.container.clear_widgets()
			if self.x == 0:
				self.x, self.y = 15, 30
			else:
				self.x, self.y = 0, 15
			main_screen_link.display_tasks()
			main_screen_link.ids.refresh_layout.refresh_done()
			self.tick = 0

		Clock.schedule_once(refresh_callback, 1)
	
	def exit_app(self):
		""" Осуществляет выход из приложения """
		self.get_running_app().stop()


if __name__ == '__main__':
	import sys
	test = False
	if "-t" in sys.argv or "--test" in sys.argv:
		test = True

	MyApp().run()
