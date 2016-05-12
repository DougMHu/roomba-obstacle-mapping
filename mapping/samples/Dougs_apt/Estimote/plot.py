import plotly.plotly as py
import plotly.graph_objs as go

# Create random data with numpy
import numpy as np

estimote_loc = [( 2.602839,  2.406666), ( 3.557685,  2.094   ), ( 2.408092,  1.089922), ( 1.079667,  0.719639), (-0.155418,  2.897234), (-0.155418,  2.897234), (-0.155418,  2.897234), (-0.155418,  2.897234), (-0.155418,  2.897234), (-0.155418,  2.897234)]
estimote_xs = [elem[0] for elem in estimote_loc]
estimote_ys = [elem[1] for elem in estimote_loc]

tmote_loc = [(0.68468468468468469, 3.9829787234042553), (0.61621621621621614, 3.9829787234042553), (0.61621621621621614, 3.9319148936170212), (0.6333333333333333, 3.965957446808511), (0.6333333333333333, 3.965957446808511), (0.6333333333333333, 3.965957446808511), (0.65045045045045036, 4.0), (0.66756756756756752, 4.0), (0.6333333333333333, 4.0170212765957451), (0.6333333333333333, 4.0170212765957451)]
tmote_xs = [elem[0] for elem in tmote_loc]
tmote_ys = [elem[1] for elem in tmote_loc]

actual_loc = [(1, 2.5), (1.5, 2.5), (1.5, 1), (2, 1), (2, 4.5), (1.5, 4.5), (1.5, 3.5), (1, 3.5), (1, 4.5), (1.5, 4.5), (1.5, 4.5)]
actual_xs = [elem[0] for elem in actual_loc]
actual_ys = [elem[1] for elem in actual_loc]

estimote_trace = go.Scatter(
    x=estimote_xs,
    y=estimote_ys,
    name='estimote',
    mode='markers',
    marker=dict(
        #color='#85144B',
        size=10
    )
)

tmote_trace = go.Scatter(
    x=tmote_xs,
    y=tmote_ys,
    name='tmote',
    mode='markers',
    marker=dict(
        #color='#85144B',
        size=10
    )
)

actual_trace = go.Scatter(
    x=actual_xs,
    y=actual_ys,
    name='actual',
    mode='markers',
    marker=dict(
        #color='#85144B',
        size=10
    )
)

data = [estimote_trace, tmote_trace, actual_trace]

py.plot(data, filename='Roomba-locations')

# or plot with: plot_url = py.plot(data, filename='basic-line')