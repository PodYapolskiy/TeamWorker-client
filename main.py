import kivy
kivy.require('2.0.0')

# Импорт из kivy
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.clipboard import Clipboard
from kivy.utils import get_color_from_hex

# Импорт из kivymd
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.picker import MDTimePicker, MDDatePicker
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import BaseSnackbar

# Импорт своих модулей из пакета project
from project.app import sign, log
from project.app import get_tasks_info, get_team_and_user_name, get_team_users, get_user_role_permissions
from project.app import push_task_info, edit_task_info, change_task_state, remove_task
from project.functions import generate_string, convert_month

# Импорт других модулей
import json
import weakref
from typing import Optional, Dict

#// (test)
from kivy.core.window import Window  # - для понимания с компьютера, убирать перед компиляцией
Window.size = (480, 840)

Config.set('kivy', 'keyboard_mode', 'systemanddock')  # открытие клавиатуры при нажатиях с телефона

delete_if_exit = True
roles = []  # Глобальный список ролей
val1, val2, val3 = False, False, False


class Singleton(type):
	"""Шаблон проектирования Одиночка. Реализация, не учитывающая метод __init__."""
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class Logger(metaclass=Singleton):
	"""Действующий авторизованный профиль. Реализует паттерн проектирования Singleton."""
	__login = None  # Логин авторизованного пользователя

	@property
	def login(self) -> Optional[str]:
		return self.__login

	@login.setter
	def login(self, value):
		self.__login = value

	__name = None

	@property
	def name(self) -> Optional[str]:
		return self.__name
	
	@name.setter
	def name(self, value):
		self.__name = value

	__team_name = None  # Название команды

	@property
	def team_name(self) -> str:
		return self.__team_name

	@team_name.setter
	def team_name(self, value):
		self.__team_name = value
	
	__role_permissions = {  # Словарь разрешений роли
		'create_tasks': True,
		'join_tasks': True,
		'inviting': True
	}

	@property
	def rp(self) -> Dict[str, bool]:
		return self.__role_permissions
	
	@rp.setter
	def rp(self, d: Dict[str, bool]):
		"""Устанавливает разрешения роли в соответствии со словарём пришедшим с сервера."""
		for k, v in d.items():
			self.__role_permissions[k] = v


account = Logger()  # Авторизованный аккаунт на клиенте. По умолчанию None


class CustomSnackbar(BaseSnackbar):
	"""Кастомный Снэкбар. Плашка, возникающая при ошибках"""
	text = StringProperty(None)
	icon = StringProperty(None)
	font_size = NumericProperty("20sp")

# -------------------------------------   Screens   -------------------------------------

class StartScreen(Screen):
	"""Начальный экран"""
	def on_enter(self):
		print("<class> StartScreen")

	def define_screens(self):
		"""Создаёт ссылки на экраны"""
		print("\t<method> define_screens\n")
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

	class SwipeToDeleteItem(MDCardSwipe, Screen):
		"""Класс карточки с пользователем"""
		text = StringProperty()
		secondary_text = StringProperty()

		def change_screen(self, instance):
			"""Функция, меняющая тексты на экране регистрации пользователя"""
			print("\t\t<method> change_screen")

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

		def set_user_box_id(self, instance):
			"""Функция, определяющая айдишник карточки"""
			print("\t\t<method> set_user_box_id")
			global user_box_id
			global sign_in_screen_link
			user_box_id = sign_in_screen_link.ids.container.children.index(instance)

		def remove_card(self, instance):
			print("\t\t<method> remove_card")
			global sign_in_screen_link
			sign_in_screen_link.ids.container.remove_widget(instance)

	class EditTeamName(BoxLayout):
		""" Текстовое поле диалогового окна """
		team_name = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.create_user_box()
		self.ids.container.children[user_box_id].text = "<Введите Ваше имя>"
		self.ids.container.children[user_box_id].secondary_text = "Капитан"

	def on_enter(self):
		print("<class> SignInScreen")
	
	def sign_in(self):
		"""Регистрация новой команды"""
		print("\t<method> sign_in")
		global data
		global roles

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
			user_login = generate_string(unique=True)
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
				account.login = user_login

		# удаляет из ролей те, которые не были использованы на момент нажатия кнопки регистрации
		for role in roles.copy():
			if role['role_name'] not in exist_roles:
				roles.remove(role)

		exist_roles.clear()  # Очищает существующие роли
		data['roles'] = roles

		print(json.dumps(data, indent=4, ensure_ascii=False))

		if sign(data):
			self.manager.transition.direction = 'down'
			self.manager.transition.duration = 0.5
			self.manager.current = 'info_screen'
		else:
			snackbar = CustomSnackbar(
				text="[color=#ffffff][b]Ошибка регистрации[/b][/color]",
				icon="information",
				bg_color="#00BFA5",
				snackbar_x="10dp",
				snackbar_y="10dp",
			)
			snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
			snackbar.open()

	def edit_team_name(self):
		""" Создаёт диалоговое окно """
		print("\t<method> edit_team_name")

		if not self.dialog:
			self.dialog = MDDialog(
				title="Команда",
				type='custom',
				content_cls=self.EditTeamName(),
				radius=[20, 20, 20, 20],
				buttons=[
					MDFlatButton(
						text="ОТМЕНА",
						on_release=self.dialog_cancel
					),
					MDRaisedButton(
						text="[color=#ffffff]ПРИНЯТЬ[/color]",
						on_release=self.dialog_accept
					),
				],
			)
			self.dialog.size_hint = 0.5, 1.0

		self.dialog.open()
	
	def dialog_cancel(self, instance):
		print("\t<method> dialog_cancel")
		self.dialog.dismiss()
	
	def dialog_accept(self, instance):
		print("\t<method> dialog_accept")
		for obj in self.dialog.content_cls.children:
			if isinstance(obj, MDTextField):
				print("\t\t", obj.text)
				self.ids.toolbar.title = obj.text
		self.dialog.dismiss()

	def clear_fields(self):
		"""Функция, меняющая все тексты в меню регистрации"""
		print("\t<method> clear_fields")
		registration_screen_link = self.manager.get_screen('registration_screen')
		registration_screen_link.ids.name.text = ""
		registration_screen_link.ids.role.text = "Роль"
		registration_screen_link.ids.label.text = "Регистрация пользователя"
		registration_screen_link.ids.button.text = "[color=#ffffff][b]ЗАРЕГИСТРИРОВАТЬ\nПОЛЬЗОВАТЕЛЯ[/b][/color]"

		registration_screen_link.ids.warning_label.text = ""  # Текст таблички, с сообщением об отсутствии текста в полях

	def create_user_box(self):
		print("\t<method> create_user_box")
		global user_box_id
		global delete_if_exit

		user_box = self.SwipeToDeleteItem()
		self.ids.container.add_widget(user_box)
		user_box_id = 0
		delete_if_exit = True

	@staticmethod
	def back_to_start():
		print('\t<staticmethod> back_to_start\n')
		screen_manager.transition.direction = 'up'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'start_screen'


class LogInScreen(Screen):
	"""Экран входa"""
	login = ObjectProperty()
	password = ObjectProperty()

	def on_enter(self):
		print("<class> LogInScreen")

		# Логин последнего зарегистрированного капитана или вошедшего пользователя
		if account.login:
			self.ids.login.text = account.login
			self.ids.password.text = ''

		#// (test)
		if test:
			self.ids.login.text = "R14987VXC3"
			self.ids.password.text = "X8VPVR8ZVK"

	def log_in(self):
		print("\t<method> log_in")

		login = self.login.text
		password = self.password.text

		data = {'login': login, 'password': password}

		if log(data):
			account.login = login  # Логин вошедшего пользователя

			rp_dict = get_user_role_permissions(login)
			if rp_dict.keys():  # Если словарь не пустой
				account.rp = rp_dict

			team_name, user_name = get_team_and_user_name(login)

			if team_name:
				account.team_name = team_name
			else:
				account.team_name = "<ОШИБКА>"

			account.name = user_name

			self.manager.transition.direction = 'up'
			self.manager.transition.duration = 0.5
			self.manager.current = 'main_screen'
		else:
			snackbar = CustomSnackbar(
				text="[color=#ffffff][b]Ошибка входа[/b][/color]",
				icon="information",
				bg_color="#00BFA5",
				snackbar_x="10dp",
				snackbar_y="10dp",
			)
			snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
			snackbar.open()

	#!!! test
	def change_to_capitan(self):
		self.ids.login.text = "T4Z1P5J3SX"
		self.ids.password.text = "EM9RFW22VS"

	def change_to_manager(self):
		self.ids.login.text = "K7YXU7MYXO"
		self.ids.password.text = "AW7647W0HY"

	def change_to_participant(self):
		self.ids.login.text = "R14987VXC3"
		self.ids.password.text = "X8VPVR8ZVK"


class RegistrationScreen(Screen):
	"""Экран регистрации пользователя"""

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

	def on_enter(self):
		print("<class> RegistrationScreen")

	def on_menu_action(self, item_text):
		print(f'\t<method> on_menu_action with text: {item_text}')

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
		print("\t<method> registrate")
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
		print("\t<method> delete_box")
		global delete_if_exit
		if delete_if_exit == True:
			print("\t\tdeleting")
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

		def open_task(self, instance):
			print("\t\t<method> open_task")

			global task_box_id
			global task_screen_link

			tasks, flag = get_tasks_info(account.login)

			self.set_task_box_id(instance)
			task = tasks[task_box_id]  # Конкретно эта задача

			task_screen_link.ids.text.text = task["task_text"]
			task_screen_link.ids.members_label.text = ", ".join(task['task_user_names'])

			date_and_time = str(task["task_deadline"]).split(" ")
			hours, minutes = date_and_time[4].split(":")[:2]  # Из "15:30:00" в "15", "30"
			day, month, year = date_and_time[1:4]

			task_screen_link.ids.time_label.text = f'{hours}:{minutes}'
			task_screen_link.ids.date_label.text = f'{day}.{convert_month(month)}.{year}'

			# Переход на экран редактирования и создания задач
			screen_manager.current = "task_screen"
			screen_manager.transition.direction = 'left'

		def set_task_box_id(self, instance):
			"""Функция, определяющая айдишник карточки"""
			print("\t\t<method> set_user_box_id")

			global task_box_id
			global main_screen_link

			children = main_screen_link.ids.container.children
			task_box_id = len(children) - 1 - children.index(instance)  #* Индексы считаются 'снизу'
			print(f"\t\t\ttask_box_id: {task_box_id}")

		def remove_card(self, instance):
			print('\t\t<method> remove_card')

			global main_screen_link
			global task_box_id

			self.set_task_box_id(instance)
			tasks, flag = get_tasks_info(account.login)

			'''Сделать через нахождения того же текста задачи
				# for task in main_screen_link.ids.container.children:
				# 	print(f"\t\t\t{task.text}")

				# for task in tasks:
				# 	print(f"\t\t\t{task['task_text']}")
				
				# print(f"tasks[{task_box_id}]:\n", json.dumps(tasks[task_box_id], indent=4, ensure_ascii=False), "\n")

				# for index, task in enumerate(tasks[::-1]):
				# 	if task['task_text'] == instance.text:
				# 		pass
				# 	print(f"\t\t\t{task['task_deadline']}")
			'''

			if remove_task(tasks[task_box_id]['task_id']):
				main_screen_link.ids.container.remove_widget(instance)
			else:
				snackbar = CustomSnackbar(
					text="[color=#ffffff][b]Ошибка удаления задачи[/b][/color]",
					icon="information",
					bg_color="#00BFA5",
					snackbar_x="10dp",
					snackbar_y="10dp",
				)
				snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
				snackbar.open()

		def on_checkbox_active(self, checkbox, value, instance):
			"""Срабатывает при изменении состояния чекбокса"""
			print("\t\t<method> on_checkbox_active")
			print(f"\t\t\tvalue: {value}")

			global task_box_id

			tasks, flag = get_tasks_info(account.login)
			# flag будем настраивать, когда приложение будет готово
			# Он нужен, чтобы корректно показывать пользователю, что именно не работает

			self.set_task_box_id(instance)
			task: dict = tasks[task_box_id]  # Задача, у которой изменяется чекбокс

			if value:
				task['task_is_done'] = True
				print("\t\t\tOn")
			else:
				task['task_is_done'] = False
				print("\t\t\tOff")

			# Если не удалось успешно изменить статус выполнения задачи, возникаем предупреждение
			if not change_task_state(task['task_id']):
				snackbar = CustomSnackbar(
					text="[color=#ffffff][b]Ошибка изменения статуса задачи[/b][/color]",
					icon="information",
					bg_color="#00BFA5",
					snackbar_x="10dp",
					snackbar_y="10dp",
				)
				snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
				snackbar.open()

	def on_enter(self):
		"""
			tasks = [
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
		print("<class> MainScreen")

		# Если пользователь не может создавать задачи и кнопка создания существует
		if (not account.rp['create_tasks']) and ('create_btn' in self.ids.keys()):
			self.ids.create_btn.parent.remove_widget(self.ids.create_btn)
			self.ids.pop('create_btn')
		
		# Если может и кнопка была удалена предыдущим пользователем
		elif (account.rp['create_tasks']) and ('create_btn' not in self.ids.keys()):

			def _on_release_create_btn(self):
				"""Функция, нужная для упаковки всех действий, которые произойдут при нажатии на MDIconButton"""
				main_screen_link.clear_screen()
				main_screen_link.change_box_id()
				screen_manager.transition.direction = 'left'
				screen_manager.transition.duration = 0.5
				screen_manager.current = 'task_screen'

			create_btn = MDIconButton(
				user_font_size="50sp",
				text_color=[1, 1, 1, 1],
				pos_hint={'x': 0.8, 'y': 0.03},
				icon="plus",
				md_bg_color=get_color_from_hex("00BFA5"),  #(colors["Teal"]["A700"]),
				theme_text_color="Custom",

				on_release=_on_release_create_btn
			)
			self.add_widget(create_btn)
			
			# До конца не понял, но всё же.
			#* Создаём слабую ссылку на кнопку, как новое значение по ключю 'create_btn'
			self.ids['create_btn'] = weakref.proxy(create_btn)

		team_name = account.team_name
		self.ids.toolbar.title = team_name

		self.ids.container.clear_widgets()
		self.display_tasks()

	def display_tasks(self):
		"""Обновляет список задач"""
		print ("\t<method> display_tasks")

		# flag - Переменная определяющая произошло ли получение задач удачно
		tasks, flag = get_tasks_info(account.login)

		# Если получение прошло без ошибок
		if flag:
			for task in tasks:
				users = [user for user in task["task_user_names"]]  # Добавляем исполняющих задачу

				date = task["task_deadline"]

				day, month, year, time = str(date).split(" ")[1:-1]
				hours, minutes = time.split(':')[:2]
				task_deadline = f"Дедлайн: {day}.{convert_month(month)}.{year[2:]} {hours}:{minutes}"

				# Добавляем карточку с заданием
				self.ids.container.add_widget(
					self.TaskCard(
							text=task["task_text"],
							secondary_text=', '.join(users),  # Строка исполнителей с разделителем ', '
							tertiary_text=task_deadline,
							active=bool(task["task_is_done"])
					)
				)
		# Если при получении произошла ошибка
		else:
			snackbar = CustomSnackbar(
				text="[color=#ffffff][b]Ошибка получения задач[/b][/color]",
				icon="information",
				bg_color="#00BFA5",
				snackbar_x="10dp",
				snackbar_y="10dp",
			)
			snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
			snackbar.open()

	def change_box_id(self):
		print("\t<method> change_box_id")
		global task_box_id
		task_box_id = len(self.ids.container.children)

	def get_tasks_length(self) -> int:
		"""Возвращает количество задач"""
		return len(self.ids.container.children)

	@staticmethod
	def back_to_log():
		print('\t<staticmethod> back_to_log\n')
		screen_manager.transition.direction = 'down'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'log_in_screen'
		
	@staticmethod
	def clear_screen():
		print('\t<staticmethod> clear_screen')
		task_screen_link.ids.text.text = ""
		task_screen_link.ids.time_label.text = "HH.MM"
		task_screen_link.ids.date_label.text = "DD.MM.YYYY"


class TaskScreen(Screen):
	_task_users_login = []  # Нужна для обмена списка логинов с <TaskMembersScreen>

	def on_enter(self):
		print("<class> TaskScreen")
		global task_box_id
		global main_screen_link

		# Если новая задача без прикреплённых участников, её текст - "..."
		if (task_box_id >= main_screen_link.get_tasks_length()) and (len(self._task_users_login) == 0):

			# Если есть право на изменение списка пользователей
			if account.rp['inviting']:
				self.ids.members_label.text = "..."
			# Если такого права нет
			else:
				self.ids.members_label.text = f"{account.name}"
				self._task_users_login.append(account.login)

		elif (task_box_id >= main_screen_link.get_tasks_length()):
			print("\tИМЕННО ЭТО")

		else:
			team_users = get_team_users(account.login)

			user_logins = team_users['user_logins']
			user_names = team_users['user_names']

			# Если ещё нет задач и есть исполнители, список исполнителей пополняется новыми значениями
			if len(main_screen_link.ids.container.children) and len(self._task_users_login):
				for user_name in str(self.ids.members_label.text).split(", "):
					index = user_names.index(user_name)
					if user_logins[index] not in self._task_users_login:
						self._task_users_login.append(user_logins[index])

	def find_errors(self) -> bool:
		"""Ищет ошибки. Удобнее было перенести логику в отдельный метод."""
		if (self.ids.text.text == "") or (self.ids.time_label.text  == "HH.MM")  or (self.ids.date_label.text == "YYYY.DD.MM") or (self.ids.members_label.text == "..."):
			return True
		return False

	def make_task(self):
		print("\t<method> make_task")
		global task_box_id  # Глобальный id-шник заданий. Равен количеству заданий.
		global main_screen_link

		print(f"\t\ttask_box_id: {task_box_id}")
		if self.find_errors():
			# self.ids.warning_label.text = "Введите все данные"
			snackbar = CustomSnackbar(
				text="[color=#ffffff][b]Введите все данные[/b][/color]",
				icon="information",
				bg_color="#00BFA5",
				snackbar_x="10dp",
				snackbar_y="10dp",
			)
			snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
			snackbar.open()
		else:
			# Данные с полей задачи
			task_text = str(self.ids.text.text)
			date = self.ids.date_label.text
			time = self.ids.time_label.text
			task_users_login = self._task_users_login

			# Редактирование задачи
			if (main_screen_link.get_tasks_length() > task_box_id):

				tasks, flag = get_tasks_info(account.login)
				print(json.dumps(tasks[task_box_id], indent=4, ensure_ascii=False))

				task = {
					"task_id": tasks[task_box_id]['task_id'],
					"task_text": None,
					"task_deadline": None,
					'task_users_login': None
				}

				# Если текст изменился, он будет отправлен
				if task_text != tasks[task_box_id]['task_text']:
					task['task_text'] = task_text

				# Если дедлайн был измененён
				date_and_time = str(tasks[task_box_id]["task_deadline"]).split(" ")
				day, month, year = date_and_time[1:4]
				hours, minutes = date_and_time[4].split(":")[:2]

				pre_date = f'{day}.{convert_month(month)}.{year}'
				pre_time = f'{hours}:{minutes}'

				if (date != pre_date) or (time != pre_time):
					task['task_deadline'] = date + " " + time

				# Если список участников был изменён
				if (task_users_login != tasks[task_box_id]['task_user_logins']):
					task['task_users_login'] = task_users_login

				
				if edit_task_info(task):
					self.ids.warning_label.text = ""
					self._task_users_login.clear()  # Обязательно очищаем этот список
					screen_manager.transition.direction = 'right'
					screen_manager.transition.duration = 0.5
					screen_manager.current = 'main_screen'
				else:
					snackbar = CustomSnackbar(
						text="[color=#ffffff][b]Ошибка редактирования задачи[/b][/color]",
						icon="information",
						bg_color="#00BFA5",
						snackbar_x="10dp",
						snackbar_y="10dp",
					)
					snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
					snackbar.open()

			# Создание новой
			else:
				task = {
					"task_text": task_text,
					# Сюда запишутся все ключи-логины из поля '__task_users_login' класса <TaskMembersScreen>
					"task_users_login": task_users_login,
					"task_deadline": date + " " + time,  # "2021.06.07 00:00" #! "06.07.2021 00:00"
					"task_is_done": False
				}

				# В функцию пуша будем класть одну задачу и отправлять на сервер
				if push_task_info(task):
					self.ids.warning_label.text = ""
					self._task_users_login.clear()  # Обязательно очищаем этот список
					screen_manager.transition.direction = 'right'
					screen_manager.transition.duration = 0.5
					screen_manager.current = 'main_screen'
				else:
					snackbar = CustomSnackbar(
						text="[color=#ffffff][b]Ошибка создания задачи[/b][/color]",
						icon="information",
						bg_color="#00BFA5",
						snackbar_x="10dp",
						snackbar_y="10dp",
					)
					snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
					snackbar.open()

	def show_time_picker(self):
		""" Открытие диалогого окна времени """
		print("\t<method> show_time_picker")

		time_dialog = MDTimePicker()
		time_dialog.bind(on_save=self.on_save_time)
		time_dialog.open()

	def on_save_time(self, instance, value):
		print(f"\t<method> on_save_time: {value}")

		time_temp_list = str(value).split(":")
		self.ids.time_label.text = f'{time_temp_list[0]}:{time_temp_list[1]}'

	def show_date_picker(self):
		""" Открытие диалогого окна даты """
		print("\t<method> show_date_picker")

		date_dialog = MDDatePicker()
		date_dialog.bind(on_save=self.on_save_date)
		date_dialog.open()

	def on_save_date(self, instance, value, date_range):
		print(f"\t<method> on_save_date: {value} {date_range}")

		date_temp_list = str(value).split("-")
		self.ids.date_label.text = f'{date_temp_list[2]}.{date_temp_list[1]}.{date_temp_list[0]}'

	def back_to_main(self):
		print('\t<method> back_to_main\n')

		# Если участники были сохранены, а задача не была сохранена и пользователь уходит через стрелку назад
		# нужно удалить всё что в это списке для корректного отображения task_members
		self._task_users_login.clear()

		screen_manager.transition.direction = 'right'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'main_screen'
	
	@staticmethod
	def edit_task_members():
		"""Если нет права на изменение списка польхователей задачи, покажет ошибку"""
		if account.rp['inviting']:
			screen_manager.transition.direction = "left"
			screen_manager.transition.duration = 0.5
			screen_manager.current = 'task_members_screen'
		else:
			snackbar = CustomSnackbar(
				text="[color=#ffffff][b]Нет права изменять участников задачи[/b][/color]",
				icon="information",
				bg_color="#00BFA5",
				snackbar_x="10dp",
				snackbar_y="10dp",
			)
			snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
			snackbar.open()


class RoleEditScreen(Screen):

	def on_enter(self):
		print("<class> RoleEditScreen")

	def on_checkbox1_active(self, checkbox, value):
		print("\tCreate_tasks: ", value)
		global val1

		if value:
			val1 = True
		else:
			val1 = False

	def on_checkbox2_active(self, checkbox, value):
		print("\tJoin_tasks: ", value)
		global val2

		if value:
			val2 = True
		else:
			val2 = False

	def on_checkbox3_active(self, checkbox, value):
		print("\tInviting: ", value)
		global val3
		
		if value:
			val3 = True
		else:
			val3 = False

	def create_role(self):
		print("\t<method> create_role")

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

	class UserInfoBox(BoxLayout, RectangularElevationBehavior):
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
			print("\t\t<method> copy_to_clipboard")
			Clipboard.copy(f"{instance.login.text}\n{instance.password.text}")
	
	def on_enter(self):
		print("<class> InfoScreen")
		print("\t<method> on_enter")
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
	
	def on_leave(self):
		"""Очищение всех полей, использующихся в регистрации команды"""
		print("\t<method> on_leave")

		#* SignInScreen
		global sign_in_screen_link
		sign_in_screen_link.ids.toolbar.title = "<Введите название команды>"

		# Удаляем всех раннее созданных польхователей для регистрации
		for user_card in sign_in_screen_link.ids.container.children.copy():
			sign_in_screen_link.ids.container.remove_widget(user_card)

		# Добавить карточку шаблон для создания нового пользователя при входе на экран регистрации
		sign_in_screen_link.create_user_box()
		sign_in_screen_link.ids.container.children[user_box_id].text = "<Введите Ваше имя>"
		sign_in_screen_link.ids.container.children[user_box_id].secondary_text = "Капитан"

		global data
		data.clear()

		# Меняет текст в диалоге на ""
		for obj in sign_in_screen_link.dialog.content_cls.children:
			if isinstance(obj, MDTextField):
				obj.text = ""

		#* RegistrationScreen
		global menu_items
		for role in menu_items.copy():
			if (role["text"] != "Капитан") and (role["text"] != "Создать роль"):
				print(f"remove: {role['text']}")
				menu_items.remove(role)
		
		# Меняем выбор ролей на дефолтный
		registration_screen_link.menu = MDDropdownMenu(
			caller=registration_screen_link.ids.role,
			items=menu_items,
			position="bottom",
			width_mult=4,
		)

		global roles
		roles.clear()

		#* RoleEditScreen
		global role_edit_screen_link
		role_edit_screen_link.ids.role_name.text = ""
		role_edit_screen_link.ids.create_tasks.active = False
		role_edit_screen_link.ids.join_tasks.active = False
		role_edit_screen_link.ids.inviting.active = False

		#* InfoScreen
		# Удаляем все созданные карточки с информацией
		for user_info in self.ids.info_list.children.copy():
			self.ids.info_list.remove_widget(user_info)


class TaskMembersScreen(Screen):
	__task_users_login = {}  # Логины пользователей участвующих в задаче: {'some_login': 'some_name'}
	__temp_dictionary = {}  # Буферный словарь. Сохраняем сюда изменения и затем либо применяем к главному словарю, либо нет

	class UserCard(MDCardSwipe, Screen):
		"""Класс карточки с пользователем"""
		text = StringProperty()
		secondary_text = StringProperty()
		active = BooleanProperty()

		class RightCheckbox(IRightBodyTouch, MDCheckbox):
			pass

		def on_checkbox_active(self, checkbox, value, instance):
			print("\t\t<method> on_checkbox_active")
			global user_logins
			global task_members_screen_link

			task_member_index = len(user_logins) - 1 - task_members_screen_link.ids.container.children.index(instance)
			print(f"\t\t\tt_m_index: {task_member_index}")
			
			print(f"\t\t\t{value}")
			if value:
				TaskMembersScreen().add_to_task_users_logins(
					login=user_logins[task_member_index],
					name=instance.ids.content.text
				)
				print("\t\t\tOn")
			else:
				TaskMembersScreen().del_from_task_users_logins(login=user_logins[task_member_index])
				print("\t\t\tOff")

	def on_enter(self):
		print("<class> TaskMembersScreen")
		global user_logins
		global user_names

		global task_box_id
		global main_screen_link
		global task_screen_link

		team_name = account.team_name
		self.ids.toolbar.title = team_name

		self.ids.container.clear_widgets()

		team_users = get_team_users(account.login)

		user_logins = team_users['user_logins']
		user_names = team_users['user_names']
		user_roles = team_users['user_roles']

		tasks, flag = get_tasks_info(account.login)

		for i in range(len(user_names)):

			flag = False
			if (main_screen_link.get_tasks_length()) > task_box_id:
				if user_names[i] in tasks[task_box_id]['task_user_names']:
					flag = True

			# В процессе создания задачи при повторном выборе участников задачи
			else:
				if user_logins[i] in task_screen_link._task_users_login:
					task_members_screen_link.__temp_dictionary[user_logins[i]] = user_names[i]
					task_members_screen_link.__task_users_login[user_logins[i]] = user_names[i]
					flag = True

			self.ids.container.add_widget(
				self.UserCard(
					text=user_names[i],
					secondary_text=user_roles[i],
					active=flag
				)
			)

	@classmethod
	def get_temp_dictionary(cls):
		print("\t<classmethod> get_temp_dictionary")
		return cls.__temp_dictionary

	@classmethod
	def get_task_users_logins(cls):
		print("\t<classmethod> get_task_users_logins")
		return cls.__task_users_login

	@classmethod
	def add_to_task_users_logins(cls, login, name):
		print("\t<classmethod> add_to_task_users_logins")
		cls.__temp_dictionary[login] = name
		print(f"\t\t{cls.__temp_dictionary}")  #// (test)
	
	@classmethod
	def del_from_task_users_logins(cls, login):
		print("\t<classmethod> del_from_task_users_logins")
		if login in cls.__temp_dictionary.keys():
			cls.__temp_dictionary.pop(login)
		print(f"\t\t{cls.__temp_dictionary}")  #// (test)

	@classmethod
	def accept_changes(cls):
		"""Копирует изменения из временного словаря в постоянный"""
		print("\t<classmethod> accept_changes")
		global user_logins
		global user_names
		global task_members_screen_link

		for task_member in task_members_screen_link.ids.container.children:
			# Проходя по каждому участнику смотрит. Если участник прикреплён к задаче,
			# то добавляет во временный словарь его логин и пароль.
			index = user_names.index(task_member.text)  # Соответстующий индекс участника
			if task_member.checkbox.active:
				task_member_login = user_logins[index]
				cls.__temp_dictionary[task_member_login] = task_member.text
			# Точно удалить из временного словаря
			else:
				if task_member.text in cls.__temp_dictionary.values():
					cls.__temp_dictionary.pop(user_logins[index])
		
		cls.__task_users_login = cls.__temp_dictionary.copy()
		print(f"\t\t__task_users_login: {cls.__task_users_login}")

		snackbar = CustomSnackbar(
			text="[color=#ffffff][b]Изменения сохранены[/b][/color]",
			icon="information",
			bg_color="#00BFA5",
			snackbar_x="10dp",
			snackbar_y="10dp",
		)
		snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
		snackbar.open()

		global task_screen_link
		task_members = ", ".join(cls.__task_users_login.values())  # 'Толя, Дима'
		if task_members == '':
			task_screen_link.ids.members_label.text = '...'
		else:
			task_screen_link.ids.members_label.text = task_members

	@classmethod
	def back_to_task(cls):
		print('\t<method> back_to_task\n')

		global task_box_id
		global main_screen_link
		global task_screen_link
		global user_logins

		#* Херня ниже работает с божьей помощью, я не понимаю
		# Если задача новая
		if (main_screen_link.get_tasks_length() <= task_box_id) and (len(task_screen_link._task_users_login) != 0):
			print("\t\tЕсли новая задача, может что-то сделать")
			task_screen_link._task_users_login = list(cls.__task_users_login.keys())
		else:
			task_screen_link._task_users_login = list(cls.__task_users_login.keys())

		# Очищаем словари
		cls.__task_users_login.clear()
		cls.__temp_dictionary.clear()

		screen_manager.transition.direction = 'right'
		screen_manager.transition.duration = 0.5
		screen_manager.current = 'task_screen'


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
		"""Обновляет состояние приложения, пока спиннер остаётся на экране"""
		print("<class> MDApp <method> refresh_callback")
		
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
		"""Осуществляет выход из приложения"""
		print("<class> MDApp <method> exit_app")
		self.get_running_app().stop()


if __name__ == '__main__':
	import sys
	test = False
	if "-t" in sys.argv or "--test" in sys.argv:
		test = True

	MyApp().run()
