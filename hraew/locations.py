from os.path import dirname, join
import wisdomhord


class LocationsBisen(wisdomhord.Bisen):

    __invoker__ = "Hrǽw"
    __description__ = "Where I've ended up"

    date = wisdomhord.Sweor("DATE", wisdomhord.Wending)
    location = wisdomhord.Sweor("LOCATION", wisdomhord.String)
    coordinates = wisdomhord.Sweor("COORDINATES", wisdomhord.Coordinate)
    purpose = wisdomhord.Sweor("PURPOSE", wisdomhord.String)


hord = wisdomhord.hladan(
    join(dirname(__file__), "horda/locations.hord"), bisen=LocationsBisen
)

locations = list(
    map(
        lambda x: {
            "date": x.date.strftime("{daeg} {month} {gere}"),
            "location": x.location,
            "purpose": x.purpose,
            "coordinates": {"lng": x.coordinates[0], "lat": x.coordinates[1]},
        },
        hord.get_rows(),
    )
)
