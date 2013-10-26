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
