from flask import Flask, render_template,request
# from search import find_lnglat_by_search


app = Flask (__name__)

# def find_lnglat_by_ip():
#     ip = request.remote_addr
#     if '127.0.0.1' == ip:
#         ip = requests.get("http://icanhazip.com/").content
#     return lat, lng


@app.route('/')
def display_firstpage():
    return render_template('firstpage.html')

@app.route('/search',  methods = ['GET'])	
def display_searchpage():
    return render_template('search.html')

@app.route('/weather', methods = ['GET', 'POST'])
def display_weather():
    c = request.form['code']
    print c  
    if request.method == 'GET':
        return render_template('weather2.html', c = 'c')

    elif request.method == 'POST':

        return  render_template('weather2.html', c = c)

app.run(debug = True)

