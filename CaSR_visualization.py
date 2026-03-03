# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 11:06:03 2026

@author: DosserH
"""
import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from matplotlib.colors import Normalize

#%% Open the CaSR files

# Path to the CaSR files and file name 
path = 'path_on_gpsc'
file_name = '1980-2024_MSC_CaSR-v3.2_AirTemp-MAvg_AGL-1.5m_RLatLon0.09_P1M.nc'

# Load the data
ds = xr.open_dataset(path+file_name, engine='netcdf4')

# Variable to plot on the map
variable_to_plot = np.squeeze(ds['AirTemp-MAvg'].mean(dim='time'))

#%% Plot the data

# Define rotated pole coordinate system
rotp = ccrs.RotatedPole(
    pole_longitude=ds.rotated_pole.grid_north_pole_longitude,
    pole_latitude=ds.rotated_pole.grid_north_pole_latitude,
)

# Extent in rotated pole coordinates 
extent = [
    ds.rlon.values.min(), 
    ds.rlon.values.max(), 
    ds.rlat.values.min(), 
    ds.rlat.values.max()
    ]

# Map projection for the plot
proj = ccrs.PlateCarree()

# Figure axes
fig, ax = plt.subplots(
    figsize=(10, 6),
    dpi=100,
    subplot_kw={'projection': rotp}
    )

# Map plot
im = ax.imshow(
    variable_to_plot, 
    norm=Normalize(vmin=-40, vmax=40),
    origin='lower', 
    extent=extent, 
    transform=rotp,
    cmap=mpl.colormaps['RdYlBu_r'].resampled(16)
    )
ax.coastlines()

# Add colorbar
cbar = plt.colorbar(
    im, ax=ax, 
    orientation="vertical", 
    shrink=0.8
    )
cbar.set_label("Temperature [$\\degree$C]")
