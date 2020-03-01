class ImgMetaData:

    def __init__(self, type: str, size: str, height: int, width: int, exif: dict):
        self.type = type
        self.size = size
        self.height = height
        self.width = width
        self.exif = exif