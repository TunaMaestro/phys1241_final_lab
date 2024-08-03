from pathlib import Path
import string
import polars as pl
import datetime

from polars.exceptions import OutOfBoundsError

from sys import argv


def open_sync(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path)
    raw = raw.with_columns(
        (pl.col("time_utc") - pl.col("time_displacement").mul(1000).cast(pl.Int64))
        .cast(pl.Datetime("ms"))
        .alias("real_time")
    )
    return raw


def open_microwave_data(data_dir: Path) -> pl.DataFrame:
    df = pl.read_csv(data_dir)
    df = df.rename({"Time": "time_offset", "Potential": "intensity"})
    return df


def open_angle_data(path: Path) -> pl.DataFrame:
    df = pl.read_csv(
        path,
        has_header=False,
    )

    df.columns = ["utc_iso", "epoch_millis", "heading"]

    df = df.with_columns(
        pl.col("utc_iso").cast(pl.Datetime("ms")),
        pl.col("epoch_millis").cast(pl.Datetime("ms")).alias("time"),
    )

    assert df.with_columns(
        (pl.col("utc_iso") == pl.col("epoch_millis")).alias("equal").all()
    )["equal"].all()

    df = df.drop("utc_iso", "epoch_millis")
    return df


def lerp(a, b, frac):
    return a + (b - a) * frac


def sync_times(angle: pl.DataFrame, intensity: pl.DataFrame) -> pl.DataFrame:
    intensity = intensity.select(["real_time", "intensity"])
    angle = angle.select(["time", "heading"])
    angle = angle.rename({"time": "real_time", "heading": "angle"})

    df = intensity.join_asof(angle, on="real_time")
    return df

    # def get_angle(t: datetime.datetime) -> pl.Float64:

    #     corresp_angle = angle.filter(pl.col("time") > t)

    #     try:
    #         angle_row = corresp_angle.row(0)
    #     except OutOfBoundsError:
    #         return float("nan")
    #     # print(angle_row)
    #     return angle_row[1]

    # mapped = intensity.with_columns(
    #     pl.col("real_time")
    #     .map_elements(get_angle, return_dtype=pl.Float64)
    #     .alias("angle")
    # )
    # mapped = mapped.filter(pl.col("angle").is_not_nan())
    return mapped


def process_trial(trial: str, data_dir: Path, manual_offset_millis=0) -> pl.DataFrame:
    trial_no = int(trial.strip(string.ascii_letters))
    print(f"Calculating data for trial {trial_no}")
    sync = open_sync(data_dir.parent / "time_sync.csv")
    microwave = open_microwave_data(data_dir / trial / "intensity.csv")
    angle = open_angle_data(data_dir / trial / "angle.csv")

    offsets = sync.row(by_predicate=pl.col("trial_no") == trial_no, named=True)

    first_data_time = offsets["real_time"]
    first_data_time += datetime.timedelta(milliseconds=manual_offset_millis)

    microwave = microwave.with_columns(
        (
            (pl.col("time_offset") * 1000).cast(pl.Duration("ms")) + first_data_time
        ).alias("real_time"),
    )

    # print(sync, microwave, angle, sep="\n\n")
    synced = sync_times(angle, microwave)

    zero_time = synced.row(0)[0]
    synced = synced.with_columns(
        (pl.col("real_time") - zero_time).alias("time").cast(pl.Int64) / 1000
    )
    print(synced)

    return synced


if __name__ == "__main__":
    data_dir = Path("lab6_data/trials")

    for i in data_dir.iterdir():
        r = process_trial(i.stem, data_dir)
        r.write_csv(i / "synced.csv")
        pass
