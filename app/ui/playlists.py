import urwid
from .tracklist import UiTracksList
from .parts import UiButton

class UiPlaylists(urwid.WidgetWrap):
	def __init__(self, ui):
		self.widget = self.build(ui)
		super(UiPlaylists, self).__init__(self.widget)
			
	def build(self, ui):
		self.ui = ui

		self.ui.setMain(urwid.Text("Получаю плейлисты"), False)
		playlists = self.ui.repository.getFeedPlaylists()

		playlistsWidgets = []

		for item in playlists:
			playlistsWidgets.append(
				urwid.Pile([
					urwid.AttrMap(urwid.Text(item.title), 'greenColor'),
					urwid.Text(item.description),
					UiButton("  →  ", on_press=self.open_playlist, user_data=item)
				])
			)

		return urwid.LineBox(urwid.Pile(playlistsWidgets), "Плейлисты")
		
	def open_playlist(self, el, data):		
		self.ui.setMain(urwid.Text("Получаю треки"), False)
		tracks = data.getTracks()	
		self.ui.setMain(UiTracksList(self.ui, tracks))		


