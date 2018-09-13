from bokeh.layouts import gridplot, Column
from bokeh.models import BooleanFilter, ColumnDataSource, CDSView, LinearAxis, Range1d
from bokeh.models import NumeralTickFormatter
from bokeh.plotting import figure, Figure

import pandas as pd

# width of the bars we use = half day in ms
w = 12 * 60 * 60 * 1000
TOOLS = "pan,wheel_zoom,box_zoom,hover,reset,save"


def make_candlesticks(price: pd.DataFrame) -> Figure:
    # adapted from https://bokeh.pydata.org/en/latest/docs/gallery/candlestick.html

    # mask, just as large as the dataframe, with True and False
    inc = price.Close > price.Open
    dec = price.Open > price.Close

    # have to fix y-range here as we are adding extra_y_range later

    p: Figure = figure(
        x_axis_type="datetime", tools=TOOLS, plot_width=1000,
        title = "ETH prices", height=400, y_range=(150, price.High.max() * 1.1))
    p.grid.grid_line_alpha = 0.7

    # line segment glyphs
    p.segment(price.Date, price.High, price.Date, price.Low, color="black")

    # green bar glyphs
    p.vbar(price.Date[inc], w, price.Open[inc], price.Close[inc],
           fill_color="#06982d", line_color="black")
    # red bar glyphs
    p.vbar(price.Date[dec], w, price.Open[dec], price.Close[dec],
           fill_color="#ae1325", line_color="black")

    return p

def make_candlesticks_cs(price: pd.DataFrame) -> Figure:
    TOOLTIPS = [
        ("index", "$index"),
        ("(x,y)", "($x, $y)"),
        ("open", "@Open"),
        ("close", "@Close")
    ]

    # have to fix y-range here as we are adding extra_y_range later
    p: Figure = figure(
        x_axis_type="datetime", tools=TOOLS, plot_width=1000, tooltips=TOOLTIPS,
        title = "ETH prices", height=400, y_range=(150, price.High.max() * 1.1))
    p.grid.grid_line_alpha = 0.7

    # this is the basic bokeh data container
    # even when we pass dataframe, CDS is created under the covers
    cds = ColumnDataSource(price)

    # line segment glyphs
    p.segment("Date", "High", "Date", "Low", color="black", source=cds)

    # green bar glyphs
    # you can't pass a mix of data source and iterable values, i.e. df + cds not gonna fly
    inc_view = CDSView(source=cds, filters=[BooleanFilter(price.Close > price.Open)])
    p.vbar("Date", w, "Open", "Close",
           fill_color="#06982d", line_color="black", source=cds, view=inc_view)

    # red bar glyphs
    dec_view = CDSView(source=cds, filters=[BooleanFilter(price.Open > price.Close)])
    p.vbar("Date", w, "Open", "Close",
           fill_color="#ae1325", line_color="black", source=cds, view=dec_view)

    return p



def add_volume_bars(price: pd.DataFrame, p: Figure) -> Figure:
    # note that we set the y-range here to be 3 times the data range so that the volume bars appear in the bottom third
    p.extra_y_ranges = {"vol": Range1d(start=price.Volume.min(), end=price.Volume.max()*3)}
    # use bottom=price.Volume.min() to have bottom of bars clipped off.
    p.vbar(price.Date, w, top=price.Volume, y_range_name="vol")
    # https://bokeh.pydata.org/en/latest/docs/reference/models/formatters.html#bokeh.models.formatters.NumeralTickFormatter
    p.add_layout(LinearAxis(y_range_name="vol", formatter=NumeralTickFormatter(format='$0,0')), 'right')
    return p


def make_volume_bars(price: pd.DataFrame) -> Figure:
    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title="ETH volume",
               y_range=(150, price.Volume.max() * 1.1))

    p.height = 150
    p.y_range = Range1d(start=price.Volume.min(), end=price.Volume.max()*1.1)
    p.yaxis[0].formatter = NumeralTickFormatter(format='$0,0')
    p.vbar(price.Date, w, top=price.Volume)

    return p


def make_linked_candlesticks_and_volume(price: pd.DataFrame) -> Column:
    c = make_candlesticks(price)
    v = make_volume_bars(price)

    v.x_range = c.x_range

    return gridplot([[c], [v]])