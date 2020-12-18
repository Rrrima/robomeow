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

def relate_list(aNode):
    tree = game.getTree()
    aGraph = nx.tree_graph(tree)
    siblings = []
    parent = list(aGraph.predecessors(aNode))
    for p in parent:
        s = list(aGraph.successors(p))
        for x in s:
            if x != aNode:
                siblings.append(x)
    relate_list = siblings + parent
    return relate_list

def fit_line(df):
    #print(df)
    if len(df['id'].unique())==0:
        return []
    curid = int(df['id'].unique()[0])
    fit = np.polyfit(df['time'],df['value'],5)
    #print(fit)
    fitx = np.arange(0,100)
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
    for i in np.arange(0,len(df['time'])):
        vals.append({'id':curid,'time':int(df['time'].iloc[i]),'value':int(df['value'].iloc[i])})
    for i in np.arange(0,len(fitx)):
        vals.append({'id':curid,'time':int(fitx[i]),'value':int(fity[i])})
    return vals

def relate_linegraph(result,aNode):
    select_si = result[result['id'].isin(relate_list(aNode))]
    rlist = select_si['id'].unique()
    vallist = []
    # selection conditions
    selection = alt.selection_single(on='mouseover',empty="none",encodings=["x"],nearest=True)
    condition1 = alt.condition(selection,alt.value(1),alt.value(0))
    selection2 = alt.selection_single(on='mouseover',empty="none",encodings=["x"])
    
    for r in rlist:
        temp_df = result[result['id']==r]
        val = fit_line(temp_df)
        vallist.extend(val)
    df_val = pd.DataFrame(vallist)
    select_id = result[result['id'] == aNode]
    # interaction line
    lg_vline = alt.Chart(df_val).mark_rule(color="#f7f1d7",size=4).encode(
        x = alt.X('time:Q'),
        opacity = condition1 
    ).add_selection(selection)

    # interaction dots
    lg_dot = alt.Chart(df_val).mark_circle(color='gray',size=70).encode(
        x = alt.X('time:Q'),
        y = alt.Y('value:Q'),
        opacity = condition1,
        tooltip = ['time:Q','value:Q']
    ).add_selection(selection2)
    p = alt.Chart(select_si).mark_point().encode(
        alt.X('time:Q', scale=alt.Scale(domain=(0, 100))),
        alt.Y('value:Q'),
        color = 'id:N'
    )
    lg = alt.Chart(df_val).mark_line().encode(
        alt.X('time:Q', scale=alt.Scale(domain=(0, 100))),
        alt.Y('value:Q'),
        color = 'id:N'
    )
    el = alt.Chart(select_id).mark_rule(color='red',strokeDash=[4,4],strokeWidth=2).encode(
        x='expires:Q'
    )
    lg_text = lg.mark_text(
        align='left',
        baseline='middle',
        dx=7,
    ).encode(
        text='value'
    ).transform_filter(
        alt.datum.time == list(select_id.expires)[0]
    )
    mark_dot = alt.Chart(df_val).mark_circle(color='red',size=50).encode(
        x = alt.X('time:Q'),
        y = alt.Y('value:Q'),
    ).transform_filter(
        alt.datum.time == list(select_id.expires)[0]
    )
    return p+el+lg + mark_dot + lg_text +  lg_vline +  lg_dot

def id_linegraph(result,id_num):
    # prepare data
    select_id = result[result['id'] == id_num]
    val = fit_line(select_id)
    df_val = pd.DataFrame(val)

    p = alt.Chart(select_id).mark_point(color='black',size=70).encode(
        alt.X('time:Q', scale=alt.Scale(domain=(0, 100))),
        alt.Y('value:Q')
    )
    
    lg = alt.Chart(df_val).mark_line(color='gray').encode(
        alt.X('time:Q', scale=alt.Scale(domain=(0, 100))),
        alt.Y('value:Q')
    )
    
    el = alt.Chart(select_id).mark_rule(color='red',strokeDash=[4,4],strokeWidth=2).encode(
        x='expires:Q'
    )
    
    lg_text = lg.mark_text(
        align='left',
        baseline='middle',
        dx=7,
    ).encode(
        text='value'
    ).transform_filter(
        alt.datum.time == list(select_id.expires)[0]
    )
    
    mark_dot = alt.Chart(df_val).mark_circle(color='red',size=50).encode(
        x = alt.X('time:Q'),
        y = alt.Y('value:Q'),
    ).transform_filter(
        alt.datum.time == list(select_id.expires)[0]
    )
    return lg + p + el + lg_text + mark_dot

def int_line(result,id_num):
    # prepare data
    select_id = result[result['id'] == id_num]
    val = fit_line(select_id)
    df_val = pd.DataFrame(val)
    # selection conditions
    selection = alt.selection_single(on='mouseover',empty="none",encodings=["x"],nearest=True)
    condition1 = alt.condition(selection,alt.value(1),alt.value(0))
    selection2 = alt.selection_single(on='mouseover',empty="none",encodings=["x"])
    # interaction line
    lg_vline = alt.Chart(df_val).mark_rule(color="lightgray",size=4).encode(
        x = alt.X('time:Q'),
        opacity = condition1 
    ).add_selection(selection)
    # interaction dots
    lg_dot = alt.Chart(df_val).mark_point(color='black',size=70,filled=True).encode(
        x = alt.X('time:Q'),
        y = alt.Y('value:Q'),
        opacity = condition1,
        tooltip = ['id:N','time:Q','value:Q']
    ).add_selection(selection2)
    return lg_vline + lg_dot

def get_pred_chart(result,rid):
    anc_chart = relate_linegraph(result,rid)
    self_chart = id_linegraph(result,rid)
    int_chart = int_line(result,rid)
    return (self_chart+int_chart)|(int_chart+anc_chart)



