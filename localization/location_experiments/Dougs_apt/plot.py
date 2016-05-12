import plotly.plotly as py
import plotly.graph_objs as go

# Create random data with numpy
import numpy as np

estimote_loc = [(3.25, 3.00), (1.67, 3.87), (2.60, 3.60), (1.53, 3.85)]
estimote_xs = [elem[0] for elem in estimote_loc]
estimote_ys = [elem[1] for elem in estimote_loc]
estimote_xs_error = [(3.16, 3.37), (1.39, 2.93), (2.04, 2.88), (1.26, 1.54)]
estimote_ys_error = [(2.71, 3.49), (2.44, 4.24), (2.78, 4.40), (3.84, 4.32)]

tmote_loc = [(1.32, 1.04), (1.32, 3.30), (0.58, 3.91), (1.95, 3.03)]
tmote_xs = [elem[0] for elem in tmote_loc]
tmote_ys = [elem[1] for elem in tmote_loc]
tmote_xs_error = [(0.0, 3.8), (0, 2.88), (0.0, 1.85), (0.0, 3.8)]
tmote_ys_error = [(0.0, 3.57), (1.33, 4.8), (2.14, 4.8), (1.74, 4.8)]

actual_loc = [(1, 1), (2, 2), (3, 3), (1, 3)]
actual_xs = [elem[0] for elem in actual_loc]
actual_ys = [elem[1] for elem in actual_loc]

estimote_trace = go.Scatter(
    x=estimote_xs,
    y=estimote_ys,
    name='estimote',
    mode='markers',
    error_x=dict(
        type='data',
        symmetric=False,
        array= [a-b for a,b in zip([elem[1] for elem in estimote_xs_error],estimote_xs)],
        arrayminus= [a-b for a,b in zip(estimote_xs,[elem[0] for elem in estimote_xs_error])],
        thickness=0.5
    ),
    error_y=dict(
        type='data',
        symmetric=False,
        array= [a-b for a,b in zip([elem[1] for elem in estimote_ys_error],estimote_ys)],
        arrayminus= [a-b for a,b in zip(estimote_ys,[elem[0] for elem in estimote_ys_error])],
        thickness=0.5
    ),
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
    error_x=dict(
        type='data',
        symmetric=False,
        array= [a-b for a,b in zip([elem[1] for elem in tmote_xs_error],tmote_xs)],
        arrayminus= [a-b for a,b in zip(tmote_xs,[elem[0] for elem in tmote_xs_error])],
        thickness=0.5
    ),
    error_y=dict(
        type='data',
        symmetric=False,
        array= [a-b for a,b in zip([elem[1] for elem in tmote_ys_error],tmote_ys)],
        arrayminus= [a-b for a,b in zip(tmote_ys,[elem[0] for elem in tmote_ys_error])],
        thickness=0.5
    ),
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

py.plot(data, filename='location-experiments')

# or plot with: plot_url = py.plot(data, filename='basic-line')