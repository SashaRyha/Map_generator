import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from haversine import haversine, Unit


def read_file() -> list:
    """
    Reads file locations.list and returns list of strings
    """
    with open("locations.list", "r") as f:
        hello = f.readlines()
    return hello[14:]


def file_lines(lines: list, year: int) -> list:
    """
    Returns list of lists of names of the films and the locations where they were made
    """
    locas = []
    for els in lines:
        try:
            film_name = els[:els.find("(")-1]
            if year == int(els[els.find("(")+1:els.find(")")]):
                splitok = els.split("\t")
                if "(" in splitok[-1]:
                    if splitok[-2][-1] == "\n":
                        locas += [[splitok[-2][:-1], film_name]]
                    else:
                        locas += [[splitok[-2], film_name]]
                else:
                    if splitok[-1][-1] == "\n":
                        locas += [[splitok[-1][:-1], film_name]]
                    else:
                        locas += [[splitok[-1], film_name]]
        except ValueError:
            continue
    return locas


def find_coordinates(locas: list, loc: list) -> list:
    """
    Returns list of lists of names of the films and the coordinates 
    of locations where they were made
    """
    geolocator = Nominatim(user_agent="main")
    loc = geolocator.reverse(str(loc)[1:-1], language="en")
    country = loc.address.split(" ")[-1]
    coordinates = []
    for els in locas:
        try:
            if country == els[0].split(" ")[-1]:
                location = geolocator.geocode(els[0])
                coordinates += [[(location.latitude,
                                  location.longitude), els[1]]]
        except AttributeError:
            continue
        except GeocoderUnavailable:
            continue
    return coordinates


def distance(coordinates: list, my_loc: list) -> list:
    """
    Returns list of 10 minimum distances between location of user and 
    locations of films and names of these films
    """
    my_loc = tuple(my_loc)
    distances = []
    for coors in coordinates:
        distances += [(haversine(coors[0], my_loc), coors[0], coors[1])]

    return sorted(distances, key=lambda coors: coors[0])[:10]


def generate_map(year: int, loc: list):
    """
    Generates map with up to 10 markers of locations where films were made
    and layer of population of countries distinguish by colors
    """
    print("Map is generating...")
    locas = file_lines(read_file(), year)
    coordinates = distance(find_coordinates(locas, loc), loc)
    map = folium.Map(location=loc)
    fg = folium.FeatureGroup(name="Markers of films")
    for coors in coordinates:
        fg.add_child(folium.Marker(
            location=[coors[1][0], coors[1][1]], popup=coors[2], icon=folium.Icon()))

    fg_pp = folium.FeatureGroup(name="Population")
    fg_pp.add_child(folium.GeoJson(data=open('world.json', 'r',
                                             encoding='utf-8-sig').read(),
                                   style_function=lambda x: {'fillColor': 'green'
                                                             if x['properties']['POP2005'] < 5000000
                                                             else 'yellow' if 5000000 <= x['properties']['POP2005'] < 10000000
                                                             else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000
                                                             else 'red' if 20000000 <= x['properties']['POP2005'] < 50000000
                                                             else 'black'}))
    map.add_child(fg_pp)
    map.add_child(fg)
    map.add_child(folium.LayerControl())
    map.save("Map_of_markers.html")
    print("Done! Now you can open the map  Map_of_markers.html")


if __name__ == "__main__":
    date = int(input("Please enter a year you would like to have a map for: "))
    loc = input("Please enter your location (format: lat, long): ").split(", ")
    loc[0] = float(loc[0])
    loc[1] = float(loc[1])
    generate_map(date, loc)
