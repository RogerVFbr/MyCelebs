from Utilities.Helpers.Helpers import Helpers as hl
from PIL.ExifTags import TAGS, GPSTAGS

class ExifUtilities:

    @classmethod
    def get_exif_data(cls, image):
        exif_data = 'N.A.'
        info = getattr(image, '_getexif', lambda: None)()
        if info:
            exif_data = {}
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    lat, lng = cls.__get_lat_lon(gps_data)
                    exif_data[str(decoded)] = {
                        'lat': lat,
                        'lng': lng
                    }

                else:
                    exif_data[str(decoded)] = value

        hl.convert_structure_content_to_strings(exif_data)
        print(f"VL - Acquired EXIF info: {exif_data}")
        return exif_data

    @classmethod
    def __get_lat_lon(cls, gps_info):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_
        data above)
        """
        lat = None
        lon = None
        gps_latitude = gps_info.get("GPSLatitude", None)
        gps_latitude_ref = gps_info.get('GPSLatitudeRef', None)
        gps_longitude = gps_info.get('GPSLongitude', None)
        gps_longitude_ref = gps_info.get('GPSLongitudeRef', None)
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = cls.__convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat
            lon = cls.__convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
        return lat, lon

    @classmethod
    def __convert_to_degrees(cls, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
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
