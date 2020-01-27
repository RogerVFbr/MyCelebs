from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image


class ExifUtilities:
    """
    Encapsulates EXIF extraction methods to be used on a Pillow Image object.
    """

    @staticmethod
    def get_exif_data(image: Image) -> dict:
        """
        Extracts and decodes EXIF data from a Pillow Image object and exposes in dictionary form.
        :param image: Pillow Image. Image to be manipulated.
        :return: dictionary. Decoded EXIF data.
        """

        # Instantiate return dictionary
        exif_data = {}

        # Attempts to extract original EXIF dictionary from Pillow Image
        info = getattr(image, '_getexif', lambda: None)()

        # If EXIF exists...
        if info:

            # Iterate on encoded keys and translate to readable keys using TAGS.
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)

                # If GPS information is found, decode it properly.
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    lat, lng = ExifUtilities.__get_lat_lon(gps_data)
                    exif_data[str(decoded)] = {
                        'lat': lat,
                        'lng': lng
                    }

                else:
                    exif_data[str(decoded)] = value

        ExifUtilities.__convert_structure_content_to_strings(exif_data)
        return exif_data

    @staticmethod
    def __get_lat_lon(gps_info: dict) -> tuple:
        """
        Decodes latitude and longitude data from given gps info dictionary.
        :param gps_info: dictionary. Contains gps coordinates information.
        :return: tuple. Decoded latitude and longitude values.
        """

        lat = None
        lon = None
        gps_latitude = gps_info.get("GPSLatitude", None)
        gps_latitude_ref = gps_info.get('GPSLatitudeRef', None)
        gps_longitude = gps_info.get('GPSLongitude', None)
        gps_longitude_ref = gps_info.get('GPSLongitudeRef', None)
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = ExifUtilities.__convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat
            lon = ExifUtilities.__convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
        return lat, lon

    @staticmethod
    def __convert_to_degrees(value: list) -> float:
        """
        Helper function to convert the GPS coordinates stored in the EXIF to degrees in standard float format.
        :param value: list. Contains coordinate in EXIF format.
        :return: float. Decoded coordinate in degrees.
        """

        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    @staticmethod
    def __convert_structure_content_to_strings(data):
        """
        Recursively convert EXIF dictionary's tuples to lists and non-integers to strings.
        :param data: multiple. Data to be processed.
        :return: multiple.
        """

        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = ExifUtilities.__convert_structure_content_to_strings(v)

        elif isinstance(data, list):
            for x in range(len(data)):
                data[x] = ExifUtilities.__convert_structure_content_to_strings(data[x])

        elif isinstance(data, tuple):
            data = list(data)
            data = ExifUtilities.__convert_structure_content_to_strings(data)

        elif isinstance(data, int):
            return data

        else:
            return str(data)

        return data
