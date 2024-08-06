from sys import argv
import polars as pl
import hvplot.pandas
import holoviews as hv
from holoviews import opts
from bokeh.plotting import show

f = argv[1]

df = pl.read_csv(f)

plot = df.plot.scatter(x=df.columns[1], y=df.columns[2])
show(hv.render(plot))
