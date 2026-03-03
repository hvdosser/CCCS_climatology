# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 08:20:11 2026

@author: Hayley Dosser

Step 1 in creating climatology files for S2D forecasts on ClimateData.ca
Script converts CaSR monthly files to monthly and seasonal files 
"""

import numpy as np
import xarray as xr


#%% User-specified parameters

# Variable and forecast period to be processed
# Monthly-averaged variables:
#   temperature = 'AirTemp-MAvg'
#   precipitation = 'Precip-Accum1h-MAvg'
# Time periods:
#   monthly = 'mon'
#   3-month season = 'sea'
var_name = 'AirTemp-MAvg'  
period = 'mon' 

# Path to the CaSR files 
path = 'path_on_gpsc'


#%% Open the CaSR files

if var_name == 'AirTemp-MAvg':
    ds = xr.open_dataset(path+'1980-2024_MSC_CaSR-v3.2_AirTemp-MAvg_AGL-1.5m_RLatLon0.09_P1M.nc', engine='netcdf4')
elif var_name == 'Precip-Accum1h-MAvg':
    ds = xr.open_dataset(path+'1980-2024_MSC_CaSR-v3.2-Analysis_Precip-Accum1h-MAvg_Sfc_RLatLon0.09_P1M.nc', engine='netcdf4') 
    
    
#%% Define functions required

def three_month_season_mean(ds):
    """
    For seasonal climatology files, convert the month coordinate to 
    3-month rolling seasons means

    Parameters
    ----------
    ds : xarray Dataset
       Data as monthly means.

    Returns
    -------
    season_mean : xarray Dataset
        Data as 3-month rolling seasonal means.
    """
    # reverse the array before applying the right-aligned rolling window
    # then reverse again to original order in time
    season_means = ds[var_name][::-1].rolling(time=3).mean()[::-1]
    
    return season_means


def month_year_split(ds):
    """
    Separate the dataset time coordinate into months and years

    Parameters
    ----------
    ds : xarray Dataset
       Data with a single time coordinate.

    Returns
    -------
    ds_time_adjust : xarray Dataset
        Data a coordinate for month and one for year.
    """
    # extract years and months
    year = ds.time.dt.year
    month = ds.time.dt.month

    # assign new coordinates
    ds = ds.assign_coords(month=("time", month.data), year=("time", year.data))

    # reshape the array to (..., "month", "year")
    ds_split = ds.set_index(time=("month", "year")).unstack("time") 
    
    return  ds_split


def reduce_spatial_extent(ds_split):
    """
    Subset the spatial extent to a box around Canada to reduce file size

    Parameters
    ----------
    ds_split : xarray Dataset
       Data over full CaSR domain.

    Returns
    -------
    ds_final : xarray Dataset
        Data in a box around Canada.
    """   
    # latitude and longitude for box around Canada
    lat_cutoff = 41.5 
    lonE_cutoff = 315
    lonW_cutoff = 215
    
    ds_final = ds_split.isel(rlat=slice(None, -1)) # CCCS-specific adjustment
    
    # Subset data to box 
    ds_final = ds_final.where(
        ds_final.lat>=lat_cutoff, drop=True
        )
    ds_final = ds_final.where(
        np.logical_and(
            ds_final.lon>=lonW_cutoff,ds_final.lon<=lonE_cutoff
            ), drop=True
        )
    
    return ds_final


#%% Pre-processing steps

# Monthly or seasonally averaged data
if period == 'mon':
    print('Data is monthly-averaged')
elif period == 'sea':
    print('Data is averaged into 3-month rolling seasons')
    ds[var_name] = three_month_season_mean(ds)
    
# Convert average total precipitation in meters per hour to millimeters per day
if var_name == 'Precip-Accum1h-MAvg': 
    ds[var_name] = ds[var_name]*1000*24
 
# Subset data to 30-year period of interest
ds_clim = ds.sel(time=slice('1991-01','2020-12'))

# Split time coordinate into months and years
ds_split = month_year_split(ds_clim)    

# Subset the spatial extent 
ds_final = reduce_spatial_extent(ds_split)

# Add necessary variables back in to final dataset
ds_final['time_bnds'] = ds_split['time_bnds']
ds_final['rotated_pole'] = ds_split['rotated_pole']
ds_final

# Rename variables in ds_final for next step in the processing
if var_name == 'Precip-Accum1h-MAvg':
    ds_final = ds_final.rename_vars({var_name: "PR"})
if var_name == 'AirTemp-MAvg':
    ds_final = ds_final.rename_vars({var_name: "TT"})
    

#%% Write to NetCDF files for further processing
if (var_name == 'Precip-Accum1h-MAvg') & (period == 'mon'):
    ds_final.to_netcdf(path+'/CaSR3P2_1991-2020_Analysis_Precip-Accum1h-Monthly_Avg_for_CCCS.nc')

if (var_name == 'AirTemp-MAvg') & (period == 'mon'):
    ds_final.to_netcdf(path+'/CaSR3P2_1991-2020_AirTemp-1.5m-Monthly_Avg_for_CCCS.nc')

if (var_name == 'Precip-Accum1h-MAvg') & (period == 'sea'):
    ds_final.to_netcdf(path+'./CaSR3P2_1991-2020_Analysis_Precip-Accum1h-Seasonal_Avg_for_CCCS.nc')

if (var_name == 'AirTemp-MAvg') & (period == 'sea'):
    ds_final.to_netcdf(path+'./CaSR3P2_1991-2020_AirTemp-1.5m-Seasonal_Avg_for_CCCS.nc')