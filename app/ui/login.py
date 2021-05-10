import urwid
from .playlists import UiPlaylists
from .parts import UiButton

class UiLogin(urwid.WidgetWrap):
	def __init__(self, ui, message = None):
		self.widget = self.build(ui, message)
		super(UiLogin, self).__init__(self.widget)

	def build(self, ui, message = None):
		self.ui = ui
		
		if (message == None):
			message = "Вход в систему"
		
		self.loginField = urwid.Edit(align="center", caption="Логин: ")
		self.passwordField = urwid.Edit(align="center", caption="Пароль: ")
		
		self.widget = urwid.LineBox(urwid.Pile([
			urwid.Text(message, align="center"),
			urwid.Text(""),
			self.loginField,
			self.passwordField,
			urwid.Text(""),
			urwid.Padding(UiButton("Войти".center(8), on_press=self.login), "center", 12)
		]))
		
		return self.widget
				
		
	def login(self, data):
		ret = self.ui.music.auth(self.loginField.edit_text, self.passwordField.edit_text)
		if ret == True:
			return self.ui.setMain(UiPlaylists(self.ui))

		return self.ui.setMain(UiLogin(self.ui, "Login failed"))

