class Location(object):
    def __init__(self, longitute=0, latitude=0,context=None, shortName=None,longName=None,streetNumber=None,route=None,locality=None,postalCode=None,country=None):
        self.longitude = longitute
        self.latitude = latitude
        self.context =context
        self.shortName = shortName
        self.longName = longName
        self.streetNumber = streetNumber
        self.route = route
        self.locality = locality
        self.postalCode = postalCode
        self.country = country