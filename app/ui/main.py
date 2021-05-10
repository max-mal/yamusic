import urwid
import sys

from ..player.player import player
from ..player.mpris import mprisManager
from .menu import UiMenu
from .login import UiLogin
from .header import UiHeader

from ..api.music import music
from ..api.repository import repository
from ..api.downloader import downloader



class Ui:
			
	def init(self):
		self.history = []
		palette = [
			('progressbar.a', 'black', 'light gray'),                        
			('buttonHighlight', 'dark red', 'black'),
			('album', 'yellow', 'default'),
			('greenColor', 'dark green', 'default'),
			('yellowColor', 'yellow', 'default'),
			('redColor', 'dark red', 'default'),
		]
		self.size = lambda rows=True, scr=urwid.raw_display.Screen(): scr.get_cols_rows()[rows]
		
		self.music = music		
		self.repository = repository		
		self.downloader = downloader
		self.player = player

		self.repository.online = music.loggedIn
				
		self.mainWidget = UiMenu(self)
		
		self.headerWidget = UiHeader(self)
		self.screen = urwid.Frame(urwid.Filler(self.mainWidget), header=self.headerWidget)
		
		
		self.loop = urwid.MainLoop(self.screen, palette, unhandled_input=self.input)
		self.history.append(self.mainWidget)

		self.loop.set_alarm_in(5, self.update_header)		
		self.loop.run()
		
	def input(self, key):
		if key == "q" or key == "Q":
			sys.exit(0)  
		if key == 'tab':
			if self.screen.get_focus() == 'header':                
				self.screen.set_focus('body')
			else:
				self.screen.set_focus('header')
		if key == "b" or key == "B":
			self.pop()

		if key == 'f1':			
			player.play()

		if key == 'f2':			
			player.pause()

		if key == 'f3':			
			player.stop()

		if key == 'f4':			
			player.prevTrack()

		if key == 'f5':			
			player.nextTrack()

		if key == 'f6':			
			player.shuffle()

		if key == 'f7':			
			player.setLoop(not player.loop)

		if key == 'f8':			
			track = player.getTrack()
			if track:
				track.like()

		if key == 'f9':			
			track = player.getTrack()
			if track:
				track.dislike()



	def setMain(self, widget, history=True):
		try:
			if history:
				self.history.append(widget)
			
			del self.mainWidget
			self.mainWidget = widget
			
			self.screen.set_body(urwid.Filler(widget))
			self.loop.draw_screen()
		except Exception as e:			
			self.screen.set_body(urwid.Filler(urwid.Text('Произошла ошибка\n' + str(e))))
			self.loop.draw_screen()
			self.history.pop()
		except:
			print('Произошла ошибка')
			self.history.pop()

	def updateHeader(self):
		
						
		# while True:			
		self.headerWidget = UiHeader(self)			
		self.screen.set_header(self.headerWidget)
		self.loop.draw_screen()
		
		pass

	def pop(self):
		if len(self.history) > 1:
			self.history.pop()
		self.setMain(self.history[len(self.history) -1 ], False)

	def update_header(self, _, __):
		# if (player.isPlaying == True):			
		self.updateHeader()
		self.loop.set_alarm_in(1, self.update_header)
				
