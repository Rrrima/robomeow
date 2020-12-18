import networkx as nx
import altair as alt
import time,json
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import Robogame as rg

game = rg.Robogame("bob")

print(alt.__version__)

def team_score():
    robots = game.getRobotInfo()
    robots['new_winner'] = robots['winner']
    robots['new_winner'] = robots['new_winner'].replace(2,'team2')
    robots['new_winner'] = robots['new_winner'].replace(-2,'unassigned')
    robots['new_winner'] = robots['new_winner'].replace(1,'team1')
    team_productivity = alt.Chart(robots).mark_bar().encode(
        alt.Y('new_winner:N'),
        alt.X('sum(Productivity):Q'),
        color='new_winner:N'
        )
    return team_productivity.properties(
						    height=60,
						    width=400
						)

def part_fit_line(df):
    #print(df)
    if len(df['value'].unique())==0:
        return []
    max_value = df['value'].max()
    min_value = df['value'].min()
    fit = np.polyfit(df['value'].astype(str).astype(float),df['Productivity'].astype(str).astype(float),1)
    #print(fit)
    #fitx = np.arange(min_value,max_value)
    fitx = np.linspace(min_value,max_value,200)
    fity = []
    fitfunc = np.poly1d(fit)
    for x in fitx:
        y = fitfunc(x)
        if (y > 100): # we know y can't be > 100
            y = 100
        if (y < 0): # we know y can't be < 0
            y = 0
        fity.append(y)
    vals = []

    for i in np.arange(0,len(fitx)):
        vals.append({'column':df['column'],'value':fitx[i],'Productivity':fity[i]})
    return vals


def plot_q_parts(part,index):
	base = alt.Chart(part_merged).mark_circle(color="black",opacity=0.1).transform_filter(
	    alt.FieldEqualPredicate(field='column', equal=f"{part}")
	).transform_filter(
	    alt.datum.winner!=-2
	).encode(
	    x=alt.X("value:Q",title=f"{part}"),
	    y=alt.Y("Productivity:Q")
	)


		# polynomial_fit = base.transform_regression(
 #        "value", "Productivity", method="poly"
 #    ).mark_line(
 #        color=f"{color_array[index]}"
 #    ).encode(
 #        #color=alt.Color("column:N",scale=color_scale),
 #        tooltip=['column'],
 #    )

	tmp_df=part_merged.loc[(part_merged['column'] == part)&(part_merged['winner'] !=-2)]
	# tmp_df=tmp_df['value','Productivity'].astype(str).astype(float)
	vals=part_fit_line(tmp_df)

	polynomial_fit = alt.Chart(alt.Data(values=vals)).mark_line(color=f"{color_array[index]}").encode(
		x='value:Q',
		y='Productivity:Q'
	)

	    
	individual = alt.Chart(part_merged).mark_rule(
	    color=f"{color_array[index]}",
	    strokeDash=[3,5],
	    size=4,
	).transform_filter(
	    alt.FieldEqualPredicate(field='column', equal=f"{part}")
	).transform_filter(
	    selection1
	).encode(
	    x=alt.X("value:Q"),
	)
	
	return alt.layer(base,polynomial_fit,individual).properties(
	    height=100,
	    width=100
	)

def plot_n_parts(part):
	base = alt.Chart(part_merged).mark_circle(opacity=0.3,color='gray').transform_filter(
	    alt.FieldEqualPredicate(field='column', equal=f"{part}")
	).transform_filter(
	    alt.datum.winner!=-2
	).encode(
	    x=alt.X("value:N",title=f"{part}"),
	    y=alt.Y("Productivity:Q")
	)
	
	bar = alt.Chart(part_merged).mark_bar(opacity=0.3).transform_filter(
	    alt.FieldEqualPredicate(field='column', equal=f"{part}")
	).transform_filter(
	    alt.datum.winner!=-2
	).encode(
	    x=alt.X("value:N"),
	    y=alt.Y("mean(Productivity):Q"),
	    tooltip=['value:N','mean(Productivity)']
	)

	individual = alt.Chart(part_merged).mark_rule().transform_filter(
	    alt.FieldEqualPredicate(field='column', equal=f"{part}")
	).transform_filter(
	    selection1
	).encode(
	    x=alt.X("value:N"),
	    color=alt.value('red'),
	    opacity=alt.condition(selection1,alt.value(1),alt.value(0)),
	)
	return base+bar+individual

def generate_time_charts():
	
	c2 = team_score()

	return c2


def generate_productivity_charts():
	global part_merged
	global pred_merged
	global degree_list
	global color_array,selection1
	global alive_robot_data

	predHints=[]
	partHints=[]
	game.getHints()
	realtimeRobotData = game.getRobotInfo()
	predHints = game.getAllPredictionHints()
	partHints = game.getAllPartHints()

	predhints_df = pd.read_json(json.dumps(predHints),orient='records')
	parthints_df = pd.read_json(json.dumps(partHints),orient='records')

	pred_merged = pd.merge(realtimeRobotData,predhints_df , how='left',
	                  left_on='id', right_on='id')
	part_merged = pd.merge(parthints_df,realtimeRobotData , how='left',
	                  left_on='id', right_on='id')
	# print("="*30)
	# print(pred_merged)
	# print("="*30)


	# selection1=alt.selection_single(empty='none',on='click',fields=['id'])
	# opacityCondition=alt.condition(selection1,alt.value(1.0),alt.value(0.6))

	# currentTime = game.getGameTime()['curtime']

	# bigBarChart = alt.Chart(pred_merged).mark_bar(size=10).encode(
	#     x=alt.X('expires:Q',sort=alt.EncodingSortField(field="expires", order='ascending')),
	#     y=alt.Y('winner',scale=alt.Scale(domain=(-2, 2))),
	#     tooltip=['id:O','expires:Q'],
	#     #opacity=alt.condition(selection1,alt.value(1.0),alt.value(0.6))
	#     color=alt.condition(selection1,alt.value('lightblue'),alt.value('lightgray'))
	# ).transform_filter(
	#     ((alt.datum.expires>currentTime-20) & (alt.datum.expires<currentTime+30))
	# ).properties(
	#     height=20,
	#     width=600
	# )

	# c1=bigBarChart.add_selection(selection1)


	selection1=alt.selection_single(empty='none',on='click',fields=['id'])
	opacityCondition=alt.condition(selection1,alt.value(1.0),alt.value(0.6))

	
	currentTime = game.getGameTime()['curtime']
	#currentTime=0

	alive_robot_data=realtimeRobotData.loc[(realtimeRobotData['id'] <100)].sort_values(by = 'expires') 

	bigBarChart = alt.Chart(alive_robot_data).mark_bar(size=4).encode(
	    # x=alt.X('id:N',sort=alt.EncodingSortField(field="expires", order='ascending')),
	    x=alt.X('id:N',sort=list(alive_robot_data['id'])),
	    y=alt.Y('winner:Q',scale=alt.Scale(domain=(-2, 2))),
	    tooltip=['id:N','expires:Q'],
	    #opacity=alt.condition(selection1,alt.value(1.0),alt.value(0.6))
	    color=alt.condition(selection1,alt.value('lightblue'),alt.value('lightgray'))
	).transform_filter(
	    # (alt.datum.expires>currentTime)
	    ((alt.datum.id<100)&(alt.datum.expires>currentTime-20) & (alt.datum.expires<currentTime+30))
	).properties(
	    height=50,
	    width=600
	)

	c1=bigBarChart.add_selection(selection1)

	# Productivity and Quantitative Parts 7 Graph
	degree_list = [1]
	q_part_list=['Repulsorlift Motor HP', 'Astrogation Buffer Length','Polarity Sinks',
	           'AutoTerrain Tread Count','InfoCore Size','Sonoreceptors','Cranial Uplink Bandwidth']
	color_scale = alt.Scale(domain=q_part_list,
	                        range=['#1FC3AA', '#8624F5','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
	color_array = ['#1FC3AA', '#8624F5','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
	qcharts = []
	i=0;
	for part in q_part_list:
	    qcharts.append(plot_q_parts(part,i))
	    i=i+1
	tmp1=alt.hconcat(qcharts[0],qcharts[1],qcharts[2],qcharts[3])
	tmp2=alt.hconcat(qcharts[4],qcharts[5],qcharts[6])
	qPartsChart = alt.vconcat(tmp1,tmp2)

	# Productivity and Nominal Parts
	n_part_list=['Arakyd Vocabulator Model', 'Axial Piston Model','Nanochip Model']
	ncharts = []
	for part in n_part_list:
	    ncharts.append(plot_n_parts(part))   
	nPartsChart = alt.hconcat(*ncharts).resolve_scale(y='shared')

	c3 = alt.Chart(alive_robot_data).mark_bar(size=4).encode(
	    x=alt.X('expires:Q',sort=list(alive_robot_data['id'])),
	    y=alt.Y('count(expires):Q'),
	).transform_filter(
	    # (alt.datum.expires>currentTime)
	    ((alt.datum.id<100)&(alt.datum.expires>currentTime-20) & (alt.datum.expires<currentTime+30))
	).properties(
	    height=50,
	    width=600
	)
	time_data = pd.DataFrame({'time': [currentTime]})

	time_line = alt.Chart(time_data).mark_rule(color='red').encode(
    x='time:Q')

	# id_text = c1.mark_text(
	#     align='left',
	#     baseline='middle',
	#     dx=7,
	# ).encode(
	#     text='id'
	# )

	# return c2&(c1+time_line)&(qPartsChart&nPartsChart)
	return (c3+time_line)&(c1)&(qPartsChart&nPartsChart)

def vis_test():
	realtimeRobotData = game.getRobotInfo()
	currentTime = game.getGameTime()['curtime']
	predHints = game.getAllPredictionHints()
	predhints_df = pd.read_json(json.dumps(predHints),orient='records')
	pred_merged = pd.merge(realtimeRobotData,predhints_df , how='left',
	                  left_on='id', right_on='id')
	# print("*"*33)
	# print(realtimeRobotData)
	# print("*"*33)
	bigBarChart = alt.Chart(pred_merged).mark_bar().transform_joinaggregate(
	    groupby=['id'],
	    count_hints='count(id)'
	).encode(
	    x=alt.X('id:O',sort=alt.EncodingSortField(field="expires", order='ascending')),
	    y=alt.Y('count_hints:Q'),
	    tooltip=['id:O','expires:Q'],
	).transform_filter(
	    (alt.datum.expires>80)
	).properties(
	    height=100,
	    width=600
	)
	# bigBarChart = alt.Chart(pred_merged).mark_bar().encode(
	# 	x=alt.X('id:O'),
	# 	y=alt.Y('expires:Q')
	# 	)
	return bigBarChart






