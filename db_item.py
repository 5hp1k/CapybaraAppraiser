class Item:
    """Класс записи базы данных"""
    def __init__(self, title, url, opinion='Neutral', comment=''):
        self.title = title
        self.url = url
        self.opinion = opinion
        self.comment = comment