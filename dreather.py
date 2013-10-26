import bottle
from settings import *
from random import shuffle
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
                     WHERE id=?', id)
    except sqlite3.ProgrammingError:
        pass


@app.route('/gimme_drink/<lat>/<lon>')
def gimme_drink(lat, lon, db):
    response = requests.get(url.format(key, lat, lon))
    cocktails = []

    sentence = "I have no idea about the weather but it's always time for a beer!"
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
                'SELECT * from sentences where min_temp<=:temp AND max_temp>=:temp'
                ' AND min_weather_rank<=:weather AND max_weather_rank>=:weather',
                {'temp': temp,
                 'weather': weather_ranks[weather]}
            ).fetchone()["sentence"]

    if not cocktails:
        cocktails = db.execute(
            'SELECT * from cocktails where name="Beer"'
        ).fetchall()

    result = map(dict, cocktails)
    shuffle(result)

    bottle.response.content_type = 'application/json'
    return json.dumps({ "cocktails" : result,
                        "sentence" : sentence})


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
