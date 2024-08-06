from pathlib import Path
import polars as pl


from pathlib import Path
import hvplot.pandas
import holoviews as hv
from holoviews import opts

labels = {
    "time": "Time (s)",
    "angle": "Angle (°)",
    "intensity": "Relative Intensity (V)",
}


def titleise(t_no):
    return f"Trial {t_no[1:]}"


if __name__ == "__main__":

    data_dir = Path("data/trials")
    for x, y in [("time", "angle"), ("angle", "intensity"), ("time", "intensity")]:
        for i in data_dir.iterdir():
            s = i / "synced.csv"
            if not s.exists():
                continue
            df = pl.read_csv(s)
            # df = df.sample(df.height / 20)
            df = df.filter(pl.col("time") > 1.0)

            plot = df.plot.scatter(
                x=x,
                y=y,
                marker="o",
                size=0.5,
                hover_cols=["time", "angle", "intensity"],
                xlabel=labels[x],
                ylabel=labels[y],
                # title=titleise(i.stem),
            )

            plot_path = (
                Path("plots") / Path(*i.parts[2:-1]) / f"{i.stem}-{x}-{y}"
            ).with_suffix(".png")
            hv.save(plot, plot_path, fmt="png")
            # hv.show(plot)
