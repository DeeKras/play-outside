import requests

def find_lnglat_by_place():
	# state = request.form[state]
	# city = request.form[postal]

	state = 'FL'
	city = 'Miami'
	api = "http://api.zippopotam.us/us/{}/{}".format(state, city)
	json_response = requests.get(api).json()
	lng = json_response['places'][0]['longitude']
	lat = json_response['places'][0]['latitude']

	return lat, lng
print find_lnglat_by_place()