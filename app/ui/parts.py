import urwid

class UiButton(urwid.WidgetWrap):
    """ Taken from https://stackoverflow.com/a/65871001/778272
    """
    def __init__(self, label, on_press=None, user_data=None, normalColor='normal', highlight='buttonHighlight', align='left'):
        self.label_widget = urwid.Text(label, align=align)
        self.widget = urwid.AttrMap(self.label_widget, normalColor, highlight)
        self.on_click = on_press   
        self.data = user_data     
        super(UiButton, self).__init__(self.widget)

    def selectable(self):
        return True

    def keypress(self, size, key):
        if (key == 'enter'):
            self.process_on_click()
            return None
        return key

    def mouse_event(self, size, event, button, x, y, focus):
        if button != 1 or not event.find("press") >= 0:
            return False

        self.process_on_click()
        return True

    def process_on_click(self):
        try:
            if (self.data == None):
                self.on_click(self)
            else:
                self.on_click(self, self.data)
        except Exception as e:            
            print(e)            

    def set_label(self, text):
        self.label_widget.set_text(text)

    def set_text(self, text):
        self.set_label(text)