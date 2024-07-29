import datetime

import numpy as np
import pandas as pd
import xarray as xr

import xarray_fmrc

initial_time = datetime.datetime(2020, 1, 1, 0, 0)
forecast_times = pd.date_range(start="2020-01-01", periods=24, freq="1h")
data = np.random.randint(980, 1000, (1, 36, 10, 10))
ds0 = xr.Dataset(
    {
        "pressure": (
            ["forecast_reference_time", "time", "lat", "lon"],
            data[:, :24, :, :],
        ),
    },
    coords={
        "lat": np.arange(10, 20),
        "lon": np.arange(-60, -50),
        "forecast_reference_time": [initial_time],
        "forecast_offset": xr.DataArray(
            [datetime.timedelta(hours=h) for h in range(24)],
            dims="time",
        ),
        "time": forecast_times,
    },
)

ds1 = xr.Dataset(
    {
        "pressure": (
            ["forecast_reference_time", "time", "lat", "lon"],
            data[:, 12:, :, :],
        ),
    },
    coords={
        "lat": np.arange(10, 20),
        "lon": np.arange(-60, -50),
        "forecast_reference_time": [initial_time + datetime.timedelta(hours=12)],
        "forecast_offset": xr.DataArray(
            [datetime.timedelta(hours=h) for h in range(24)],
            dims="time",
        ),
        "time": forecast_times + datetime.timedelta(hours=12),
    },
)


def test_from_model_path(ds0=ds0, ds1=ds1):
    xarray_fmrc.from_model_runs([ds0, ds1])


def test_constant_forecast(ds0=ds0, ds1=ds1):
    dt = xarray_fmrc.from_model_runs([ds0, ds1])
    ds = dt.fmrc.constant_forecast("2020-01-01 12:00:00")

    assert (
        np.all(ds.pressure.diff(dim="forecast_reference_time")) == 0
    ), "Forecasts at 12:00:00 should be the same"


def test_constant_offset(ds0=ds0, ds1=ds1):
    dt = xarray_fmrc.from_model_runs([ds0, ds1])
    ds = dt.fmrc.constant_offset("1h")

    assert ds.forecast_offset.shape == (), "The forecast_offset should be a scalar"
    assert isinstance(
        ds["forecast_offset"].values,
        np.timedelta64,
    ), "The forecast_offset should be of time np.timedelta"
    assert ds.time.forecast_offset == np.timedelta64(
        datetime.timedelta(hours=1),
    ), "Forecast offset should be 1 hour"
