import urwid
from .playlists import UiPlaylists
from .search import UiSearch
from .tracklist import UiTracksList
from ..database.models.track import TrackModel
from .parts import UiButton

class UiMenu(urwid.WidgetWrap):
	def __init__(self, ui):
		self.widget = self.build(ui)
		super(UiMenu, self).__init__(self.widget)

	def build(self, ui):
		self.ui = ui
		return urwid.LineBox(urwid.Pile([
			UiButton("Плейлисты    →", on_press=self.playlists),
			UiButton("Поиск        →", on_press=self.search),
			UiButton("Загруженное  →", on_press=self.downloaded),
			UiButton("Мне нравится  →", on_press=self.liked),
		]), 'Меню')

	def playlists(self, data):
		self.ui.setMain(UiPlaylists(self.ui))

	def search(self, el):
		self.ui.setMain(UiSearch(self.ui))		

	def downloaded(self, el):
		self.ui.setMain(urwid.Text("Получаю треки"), False)
		tracks = TrackModel.query('where is_downloaded = 1')
		self.ui.setMain(UiTracksList(self.ui, tracks, showDownload=False))

	def liked(self, el):
		from ..api.repository import repository
		self.ui.setMain(urwid.Text("Получаю треки"), False)
		tracks = repository.getLikedTracks()
		self.ui.setMain(UiTracksList(self.ui, tracks))
