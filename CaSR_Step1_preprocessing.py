# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 08:20:11 2026

@author: Hayley Dosser (with edits by Julia Velletta)

Step 1 in creating climatology files for S2D forecasts on ClimateData.ca
Script converts CaSR monthly files to monthly, seasonal, or decadal files 
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
#   5-year decadal = [ 'dcp_Ann', 'dcp_MJJAS', 'dcp_NDJFM' ]

var_name = 'AirTemp-MAvg'  
period = 'dcp_NDJFM' 

# Path to the CaSR files 
input_path = '/fs/site8/eccc/cmd/cmdw/vpo018/data_sharing/reanalysis_casr/casr/v3.2/post-processing/grid/'
output_path = '/home/rjj000/site7/CCCS_CDca/CaSR_Climatology/Step1'


#%% Open the CaSR files

if var_name == 'AirTemp-MAvg':
    ds = xr.open_dataset(f'{input_path}1980-2024_MSC_CaSR-v3.2_AirTemp-MAvg_AGL-1.5m_RLatLon0.09_P1M.nc', engine='netcdf4')
elif var_name == 'Precip-Accum1h-MAvg':
    ds = xr.open_dataset(f'{input_path}1980-2024_MSC_CaSR-v3.2-Analysis_Precip-Accum1h-MAvg_Sfc_RLatLon0.09_P1M.nc', engine='netcdf4') 

ds_orig = ds.copy()
    
    
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


def decadal_means(ds, number_of_years=5, length_of_season=12, first_month=1):
    """
    Compute rolling multi-year seasonal means from a monthly dataset.

    Parameters
    ----------
    ds : xarray.Dataset
        Monthly dataset containing a ``time`` coordinate of type datetime64.
    number_of_years : int, optional
        Length of the rolling averaging window in years (default is 5).
    length_of_season : int, optional
        Number of consecutive months in the season (1-12). Default is 12,
        corresponding to the full annual mean.
    first_month : int, optional
        First month of the season (1-12). For example, ``first_month=11`` and
        ``length_of_season=5`` defines the season November-March.

    Returns
    -------
    xarray.DataArray or xarray.Dataset
        Dataset containing rolling multi-year seasonal means.
        Each year represents the average over the interval:
        ``year → year + number_of_years - 1`` (e.g., 1991 = mean of 1991-1995)
        The output is restricted to the climatological baseline period
        1991-2020, adjusted for the length of the rolling window.
    """
    
    selected_months = [(first_month + i - 1) % 12 + 1 for i in range(length_of_season)]
    yr_crossover = max(0, first_month + length_of_season - 13)
        
    # subset only valid months in season
    ds_season = ds.sel(time=ds.time.dt.month.isin(selected_months))

    # create a "season year" coordinate
    ds_season = ds_season.assign_coords(
        season_year = ds_season.time.dt.year - (ds_season.time.dt.month <= yr_crossover)
    )

    # take seasonal mean
    season_mean = ds_season.groupby("season_year").mean("time")

    # take 5-year mean
    season_5yr = (
        season_mean
        .rolling(season_year=number_of_years, center=False)
        .mean()
        .shift(season_year=-(number_of_years-1))
        .dropna("season_year")
    )

    season_5yr = season_5yr.rename(season_year="year")

    ds_clim = season_5yr.sel(year=slice(1991, 2020-(number_of_years-1)))

    return ds_clim


#%% Pre-processing steps

# Monthly or seasonally averaged data
if period == 'mon':
    print('Data is monthly-averaged')

elif period == 'sea':
    print('Data is averaged into 3-month rolling seasons')
    ds[var_name] = three_month_season_mean(ds)

elif period == 'dcp_Ann':
    print('Data is averaged into 5-year periods - Ann (full year)')
    ds[var_name] = decadal_means(ds[var_name])

elif period == 'dcp_MJJAS':
    print('Data is averaged into 5-year periods - MJJAS (extended warm season)')
    ds[var_name] = decadal_means(ds[var_name], 5, 5, 5)

elif period == 'dcp_NDJFM':
    print('Data is averaged into 5-year periods - NDJFM (extended cold season)')
    # ds[var_name] = decadal_means(ds[var_name], 5, 5, 11)  # use for NDJFM Yr1-5 forecasts
    ds[var_name] = decadal_means(ds[var_name], 4, 5, 11)  # alternative for NDJFM Yr6-10 forecasts

# Convert average total precipitation in meters per hour to millimeters per day
if var_name == 'Precip-Accum1h-MAvg': 
    ds[var_name] = ds[var_name]*1000*24
 
if period[:3] == 'dcp': 
    ds_split = ds

else:
    # Subset data to 30-year period of interest
    ds_clim = ds.sel(time=slice('1991-01','2020-12'))

    # Split time coordinate into months and years
    ds_split = month_year_split(ds_clim)    

# Subset the spatial extent 
ds_final = reduce_spatial_extent(ds_split)

# Add necessary variables back in to final dataset
ds_final['time_bnds'] = ds_orig['time_bnds']
ds_final['rotated_pole'] = ds_orig['rotated_pole']

# Rename variables in ds_final for next step in the processing
if var_name == 'Precip-Accum1h-MAvg':
    ds_final = ds_final.rename_vars({var_name: "PR"})
if var_name == 'AirTemp-MAvg':
    ds_final = ds_final.rename_vars({var_name: "TT"})
    

#%% Write to NetCDF files for further processing
if (period == 'mon'):
    if (var_name == 'Precip-Accum1h-MAvg'):
        ds_final.to_netcdf(f'{output_path}/CaSR3P2_1991-2020_Analysis_Precip-Accum1h-Monthly_Avg_for_CCCS.nc')
    elif (var_name == 'AirTemp-MAvg'):
        ds_final.to_netcdf(f'{output_path}/CaSR3P2_1991-2020_AirTemp-1.5m-Monthly_Avg_for_CCCS.nc')

elif (period == 'sea'):
    if (var_name == 'Precip-Accum1h-MAvg'):
        ds_final.to_netcdf(f'{output_path}/CaSR3P2_1991-2020_Analysis_Precip-Accum1h-Seasonal_Avg_for_CCCS.nc')
    elif (var_name == 'AirTemp-MAvg'):
        ds_final.to_netcdf(f'{output_path}/CaSR3P2_1991-2020_AirTemp-1.5m-Seasonal_Avg_for_CCCS.nc')

elif (period[:3] == 'dcp'):
    if (var_name == 'Precip-Accum1h-MAvg'):
        ds_final.to_netcdf(f'{output_path}/CaSR3P2_1991-2020_Analysis_Precip-Accum1h-Decadal-{period[4:]}-alt_Avg_for_CCCS.nc')
    elif (var_name == 'AirTemp-MAvg'):
        ds_final.to_netcdf(f'{output_path}/CaSR3P2_1991-2020_AirTemp-1.5m-Decadal-{period[4:]}-alt_Avg_for_CCCS.nc')