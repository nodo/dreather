import bottle
from settings import *
import random
import requests
import bottle.ext.sqlite
import simplejson as json
import sqlite3

app = bottle.Bottle()
plugin = bottle.ext.sqlite.Plugin(dbfile='dreather.db')
app.install(plugin)


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='client')

@app.route('/')
def index():
    return bottle.static_file('index.html', root='client')

@app.post('/pump_it_up/<id>')
def pump_it_up(id, db):
    try:
        db.execute( 'UPDATE cocktails\
                     SET rank=rank+1\
                     WHERE id=:id', {'id' : id })
    except sqlite3.ProgrammingError:
        pass

def random_dist(cocktails):
    """Shuffle cocktails taking into account weights"""
    random.shuffle(cocktails)
    shuffled_cocktails = []
    for i in range(len(cocktails)):
        total = float(sum(int(cocktail["rank"]) for cocktail in cocktails))
        #force probability to be at least 0.1, right way to do it
        #minimum_rank = min(int(cocktail["rank"]) for cocktail in cocktails)
        #magic_number = float((total-10*minimum_rank) / (10-len(cocktails)))
        #force a minimum probability, safe way to do it ;-)
        magic_number = 5
        total += len(cocktails) * magic_number

        rand = random.randint(0,total)
        tot = 0
        for j in range(len(cocktails)):
            cocktail = cocktails[j]
            tot += int(cocktail["rank"])+magic_number
            if tot>=rand:
                shuffled_cocktails.append(cocktail)
                cocktails.remove(cocktail)
                break
    return shuffled_cocktails


def gimme_drink(lat, lon, db):
    response = requests.get(url.format(key, lat, lon))
    cocktails = []
    weather = "N/A"
    temp = "N/A"
    city = "N/A"

    sentence = "I have no idea about the weather but it's always time for a beer!"
    try:
        city = response.json()['current_observation']['display_location']['full']
    except KeyError:
        pass

    try:
        temp     = response.json()['current_observation']['temp_c']
        weather  = response.json()['current_observation']['weather']
    except KeyError:
        pass
    else:
        if weather in weather_ranks:
            cocktails = db.execute(
                'SELECT * from cocktails where min_temp<=:temp AND max_temp>=:temp'
                ' AND min_weather_rank<=:weather AND max_weather_rank>=:weather',
                {'temp': temp,
                 'weather': weather_ranks[weather]}
            ).fetchall()
            sentence = db.execute(
                'SELECT * from sentences where min_temp<=:temp AND max_temp>=:temp'
                ' AND min_weather_rank<=:weather AND max_weather_rank>=:weather',
                {'temp': temp,
                 'weather': weather_ranks[weather]}
            ).fetchone()["sentence"]
        else:
            cocktails = db.execute(
                'SELECT * from cocktails where min_temp<=:temp AND max_temp>=:temp',
                {'temp': temp}
            ).fetchall()
            sentence = db.execute(
                'SELECT * from sentences where min_temp<=:temp AND max_temp>=:temp',
                {'temp': temp }
            ).fetchone()["sentence"]

    if not cocktails:
        cocktails = db.execute(
            'SELECT * from cocktails where name="Beer"'
        ).fetchall()

    result = map(dict, cocktails)
    result = random_dist(result)

    bottle.response.content_type = 'application/json'
    return json.dumps({ "cocktails" : result,
                        "sentence" : sentence,
                        "weather" : weather,
                        "temperature" : temp,
                        "city" : city,
                        "lat" : lat,
                        "lon" : lon
                    })

@app.route('/gimme_drink/<station_code>')
def gimme_drink_with_station(station_code, db):
    response = requests.get(station_url.format(key, station_code))
    try:
        lat = response.json()['current_observation']['display_location']['latitude']
        lon = response.json()['current_observation']['display_location']['longitude']
    except KeyError:
        lat = 0
        lon = 0
    return gimme_drink(lat, lon, db)


@app.route('/gimme_drink/<lat>/<lon>')
def gimme_drink_with_latlon(lat, lon, db):
    return gimme_drink(lat, lon, db)


def rank_to_png(arank):
    # return the name of an iamge corresponding to the rank_weather
    rank_to_png = {
            1 : "chance-storm-n.png",
            2 : "chance-storm.png",
            3 : "blizzard.png",
            4 : "blizzard.png",
            5 : "blizzard.png",
            6 : "blizzard.png",
            7 : "blizzard.png",
            8 : "freezing-rain.png",
            9 : "freezing-rain.png",
            10 : "rainy-snow.png",
            11 : "rainy-snow.png",
            12 : "blizzard.png",
            13 : "blizzard.png",
            14 : "blizzard.png",
            15 : "blizzard.png",
            16 : "rainy-snow.png",
            17 : "rainy-snow.png",
            18 : "snow.png",
            19 : "snow.png",
            20 : "snow.png",
            21 : "snow.png",
            22 : "snow.png",
            23 : "snow.png",
            24 : "sleet.png",
            25 : "sleet.png",
            26 : "thunderstorm.png",
            27 : "thunderstorm.png",
            28 : "t-storm-rain.png",
            29 : "t-storm-rain.png",
            30 : "rainy.png",
            31 : "p-c-rain.png",
            32 : "rainy.png",
            33 : "p-c-rain.png",
            34 : "m-c-night-rain.png",
            35 : "m-c-night-rain.png",
            36 : "drizzle.png",
            37 : "fair-drizzle.png",
            38 : "fair-drizzle.png",
            39 : "fair-drizzle.png",
            40 : "fog.png",
            41 : "fog.png",
            42 : "cloudy.png",
            43 : "partly-clouy.png",
            44 : "partly-clouy.png",
            45 : "wind.png",
            46 : "sunny.png"
    }
    if (arank > 0 and arank < len(rank_to_png)):
        return rank_to_png[arank]
    else:
        return -1


app.run(host='localhost', port=8080)
