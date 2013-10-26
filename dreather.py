from bottle import *
from settings import *
import requests
import bottle.ext.sqlite
import simplejson as json

app = bottle.Bottle()
plugin = bottle.ext.sqlite.Plugin(dbfile='dreather.db')
app.install(plugin)

@app.route('/')
def index():
    return 'Beer!'

@app.route('/gimme_drink/<lat>/<lon>')
def gimme_drink(lat, lon, db):
    response = requests.get(url.format(key, lat, lon))
    temp     = response.json()['current_observation']['temp_c']
    weather  = response.json()['current_observation']['weather']

    if weather in weather_ranks:
        cocktails = db.execute(
            'SELECT * from cocktails where min_temp<=:temp AND max_temp>=:temp\
             AND min_weather_rank<=:weather AND max_weather_rank>=:weather',
            {'temp' : temp,
             'weather' : weather_ranks[weather]}
        ).fetchall()
    else:
        cocktails = db.execute(
            'SELECT * from cocktails where min_temp<=:temp AND max_temp>=:temp',
            {'temp' : temp}
        ).fetchall()

    if cocktails:
        return json.dumps({ "cocktails" : map(dict, cocktails)})
    return HTTPError(404, "Page not found")

app.run(host='localhost', port=8080)
