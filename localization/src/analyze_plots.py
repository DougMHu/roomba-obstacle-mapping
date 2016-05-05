import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot
import numpy as np
import json

def extract_rssi(filename):
    # Load JSON output
    with open(filename, "r") as f: 
        data = json.load(f)

    # Extract lists
    dist = float(data.keys()[0])
    adict = data.values()[0]
    rssi_list = adict.values()[0]

    return rssi_list

x_theo = np.linspace(0, 8, 100)
sincx = np.sinc(x_theo)

x = [0.5, 1, 2, 3, 4, 8]
y = [1.0, 0.125, 4.0, 2.97198857827, 5.65685424949, 5.27803164309]
UBE = [1.237726285305428, 1.0, 5.508037804777077, 5.508037804777077, 5.943977156547793, 8]
LBE = [0.9057236642639067, 0.0625, 2.4754525706108557, 2.109532152963293, 3.363585661014858, 5.27803164309]
#x = [-3.8, -3.03, -1.91, -1.46, -0.89, -0.24, -0.0, 0.41, 0.89, 1.01, 1.91, 2.28, 2.79, 3.56]
#y = [-0.02, 0.04, -0.01, -0.27, 0.36, 0.75, 1.03, 0.65, 0.28, 0.02, -0.11, 0.16, 0.04, -0.15]

trace1 = go.Scatter(
    x=x_theo,
    y=x_theo,
    name='ideal'
)
trace2 = go.Scatter(
    x=x,
    y=y,
    mode='markers',
    name='measured',
    error_y=dict(
        #type='constant',
        #value=0.2,
        type='data',
        symmetric=False,
        array= [a-b for a,b in zip(UBE,y)], #UBE - y,
        arrayminus= [a-b for a,b in zip(y,LBE)], #y - LBE,
        color='#85144B',
        thickness=1.5,
        width=3,
        opacity=1
    ),
    marker=dict(
        color='#85144B',
        size=8
    )
)
data = [trace1, trace2]
fig = go.Figure(data=data)
fig['layout'].update(
    title="Distance Estimation using RSSI model",
    xaxis=dict(ticks='', title='Actual Distance'),#, side='top'),
    # ticksuffix is a workaround to add a bit of padding
    yaxis=dict(ticks='', ticksuffix='  ',title='Estimated Distance') )#,
    #width=700,
    #height=700,
    #autosize=False)
plot_url = py.plot(fig, filename='distance_plot.html')

# Box and Whisker plot
filenames = ["experiment05.json", "set2/experiment1.json", "experiment2.json", 
            "experiment3.json", "set2/experiment4.json", "set2/experiment8.json"]
distances = ["0.5 m", "1 m", "2 m", "3 m", "4 m", "8 m"]
rssi_lists = [extract_rssi(f) for f in filenames]
#x0 = np.random.randn(50)
#x1 = np.random.randn(50) + 2

#trace0 = Box(x=x0)
#trace1 = Box(x=x1)
data = [go.Box(x=x, name=distance) for x,distance in zip(rssi_lists,distances)]
fig = go.Figure(data=data)
fig['layout'].update(
    title="RSSI for each distance",
    xaxis=dict(ticks='', title='RSSI'))
plot_url = py.plot(fig, filename='rssi_plot.html')




