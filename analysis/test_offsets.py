from sync import process_trial

from pathlib import Path
import polars as pl


from pathlib import Path
import hvplot.pandas
import holoviews as hv
from holoviews import opts
from bokeh.plotting import show


if __name__ == "__main__":
    data_dir = Path("lab6_data/trials")

    offset_tries = 200
    for i in range(offset_tries):
        df = process_trial(
            "t7", data_dir, manual_offset_millis=(i - offset_tries) * 1000
        )
        df.write_csv("tests/t2/synced.csv")
        plot = df.plot.scatter(
            x="angle",
            y="intensity",
            marker="o",
            size=0.5,
            hover_cols=["time", "angle", "intensity"],
        )
        show(hv.render(plot))
