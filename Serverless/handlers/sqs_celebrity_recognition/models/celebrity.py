class Celebrity:

    def __init__(self, name, recognition_id, bounding_box, urls):
        self.name = name
        self.table_id = name.lower().replace(' ', '-')
        self.recognition_id = recognition_id
        self.bounding_box = bounding_box
        self.urls = urls
