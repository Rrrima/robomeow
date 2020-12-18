import flask
from flask import request, jsonify, render_template, redirect
import pandas as pd
import numpy as np
from flask_cors import CORS
import Robogame as rg
import networkx as nx
import altair as alt
import time,json
import time
import nx_altair as nxa
from apscheduler.schedulers.background import BackgroundScheduler
import time
from pred_vis import get_pred_chart,relate_list
from part_vis import generate_productivity_charts,generate_time_charts

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
# grab the networks
global rid_hints
rid_hints = 0

def print_robots():
	global robot
	robots = game.getRobotInfo()
	hints = game.getHints()
	team1 = list(robots[robots['winner']==1]['id'])
	team2 = list(robots[robots['winner']==2]['id'])
	# print('='*20,'team1 robots','='*20)
	# print(team1)
	# print('='*20,'team2 robots','='*20)
	# print(team2)

def start_game():
	# create a game connection using bob as the "secret" key for your team (this is what you're given by the server)
	global game 
	game = rg.Robogame("meowww")
	# game = rg.Robogame("meowww",server="12.12.31.1",port=2324)
	# tell the server we're ready to go
	game.setReady()
	# wait for both players to be ready
	while(True):
	    gametime = game.getGameTime()
	    timetogo = gametime['gamestarttime_secs'] - gametime['servertime_secs']
	    
	    if ('Error' in gametime):
	        print("Error"+str(gametime))
	        break
	    if (timetogo <= 0):
	        print("Let's go!")
	        break
	        
	    print("waiting to launch... game will start in " + str(int(timetogo)))
	    time.sleep(1) # sleep 1 second at a time, wait for the game to start

def set_initial():
	bets = {}
	for i in np.arange(0,100):
		bets[int(i)] = int(50)
	game.setBets(bets)


@app.route('/', methods=['GET','POST'])
def home():
	return render_template('index.html')

@app.route('/predhint', methods=['POST'])
def get_predids():
	if request.method == 'POST':
		pred = request.form['predid']
		pred = [int(each) for each in pred.split(' ')]
		game.setRobotInterest(pred)
		print("="*20)
		print(pred)
		hints = game.getHints()
		if 'predictions' in hints:
			print([x['id'] for x in hints['predictions']])
		return redirect('/')

@app.route('/parthint', methods=['POST'])
def get_partnames():
	if request.method == 'POST':
		pred = request.form.getlist('partname')
		game.setPartInterest(pred)
		print("="*20)
		print(pred)
		hints = game.getHints()
		if 'parts' in hints:
			print([x['column'] for x in hints['parts']])
		return redirect('/')

@app.route('/rid', methods=['POST','GET'])
def get_network():
	global rid
	print("%"*30)
	print(rid)
	if request.method == 'POST':
		rid = int(request.form['rid'])
	return redirect('/')

@app.route('/score', methods=['POST','GET'])
def get_score():
	global rid
	if request.method == 'POST':
		score = int(request.form['score'])
	result = game.setBets({rid:score})
	return redirect('/')

@app.route('/network')
def vis_network():
	global rid
	print("="*20)
	print(rid)
	print("="*20)
	for n in socialnet.nodes():
		socialnet.nodes[n]['weight'] = socialnet.degree[n]
		socialnet.nodes[n]['id'] = n
		socialnet.nodes[n]['owner'] = int(robots[robots['id']==n].winner)
	neighbors = [n for n in socialnet.neighbors(rid)]
	neighbors.append(rid)
	G = socialnet.subgraph(neighbors)
	network_chart = nxa.draw_networkx(
	    G,
	    node_color='owner:N',
	    cmap='accent',
	    edge_color='#d7dcde',
	    node_size = 'weight',
	    node_tooltip = ['id','owner','weight'],
	).properties(width=200,height=200)
	# get ancester graph
	relatelist = relate_list(rid)
	relatelist.append(rid)
	aG = aGraph.subgraph(relatelist)
	for n in aGraph.nodes():
		aGraph.nodes[n]['id'] = n
		aGraph.nodes[n]['owner'] = int(robots[robots['id']==n].winner)
	relate_chart = nxa.draw_networkx(
	    aG,
	    node_color='owner:N',
	    cmap='accent',
	    edge_color='#d7dcde',
	    node_tooltip = ['id','owner'],
	).properties(width=200,height=200)
	combined_chart = network_chart | relate_chart
	return combined_chart.to_json()

@app.route('/hint/rid', methods=['POST','GET'])
def get_hintsrid():
	global rid_hints
	if request.method == 'POST':
		rid_hints = int(request.form['rid_hint'])
		print(rid_hints)
	return redirect('/')

@app.route('/hint', methods=['POST','GET'])
def vis_pred():
	global predHints
	global partHints
	global robots
	robots = game.getRobotInfo()
	game.getHints()
	predHints = game.getAllPredictionHints()
	partHints = game.getAllPartHints()
	predhints_df = pd.read_json(json.dumps(predHints),orient='records')
	result = pd.merge(predhints_df, robots, how='left', on=['id'])
	pred_chart = get_pred_chart(result,rid)
	return pred_chart.to_json()

@app.route('/times', methods=['POST','GET'])
def vis_time():
	# part_chart = generate_productivity_charts()
	time_chart = generate_time_charts()
	return time_chart.to_json()

@app.route('/parts', methods=['POST','GET'])
def vis_part():
	# part_chart = generate_productivity_charts()
	part_chart = generate_productivity_charts()
	return part_chart.to_json()

if __name__ == '__main__':
	start_game()
	set_initial()
	scheduler = BackgroundScheduler()
	scheduler.add_job(func=print_robots, trigger="interval", seconds=6)
	scheduler.start()
	network = game.getNetwork()
	tree = game.getTree()
	socialnet = nx.node_link_graph(network)
	aGraph = nx.tree_graph(tree)
	rid = 0
	app.run(port=8000)








