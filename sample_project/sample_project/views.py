from opress.views import IndexView

class MyIndexView(IndexView):
    def get_additional_content(self):
        return {}