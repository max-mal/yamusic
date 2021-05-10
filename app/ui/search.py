import urwid
from .search_results import UiSearchResults
from .parts import UiButton

class UiSearch(urwid.WidgetWrap):
	def __init__(self, ui):
		self.widget = self.build(ui)
		super(UiSearch, self).__init__(self.widget)
		
	def build(self, ui):
		self.ui = ui
		
		
		self.searchField = urwid.Edit(align="center", caption="Поиск: ")		
		
		self.widget = urwid.LineBox(urwid.Pile([						
			self.searchField,			
			urwid.Text(""),
			urwid.Padding(UiButton("Искать".center(8), on_press=self.search), "center", 12)
		]))
		
		return self.widget
				
		
	def search(self, data):
		if (len(self.searchField.edit_text) < 3):
			return

		from ..api.repository import repository
		self.ui.setMain(urwid.Text('Выполняется поиск'), False)	
		response = repository.search(self.searchField.edit_text)	
		self.ui.setMain(UiSearchResults(self.ui, response))	

