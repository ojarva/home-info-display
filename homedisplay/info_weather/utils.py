from astral import Astral

def get_sun_info():
    sun_info = Astral()
    sun_info.solar_depression = 'civil'
    b = sun_info[settings.SUN_CITY].sun()
    return b
