# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 08:48:19 2025

Step 3 in creating climatology files for seasonal forecasts on ClimateData.ca
Script regrids the percentiles of the CaSR climatology 

@author: DosserH
"""

import xarray as xr
import xesmf as xe

# Paths to grid and data
grid_path = 'path_to_grid_on_gpsc'
data_path = 'path_to_data_on_gpsc'

# Load the CD.ca grid and create the target grid for regridding
dg = xr.open_dataset(grid_path+'m6_grid.nc', engine='netcdf4') 
dg_target = xr.Dataset(
    {
        "lat": (["lat"], dg.lat.values, {"units": "degrees_north"}),
        "lon": (["lon"], dg.lon.values, {"units": "degrees_east"}),
    }
)

# Loop over variables:  temperature 'TT' and precipitation 'PR'
# Loop over monthly 'mon', 3-month seasonal 'sea', and 5-year decadal 'dcp' time periods
var_name = ['TT', 'PR']
period = ['mon', 'sea', 'dcp_Ann', 'dcp_MJJAS', 'dcp_NDJFM']
for i, n in enumerate(var_name):
    for j, m in enumerate(period):

        # Load the data
        if (n == 'TT') & (m == 'mon'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Monthly/UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Monthly/LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Monthly/Percentiles_parametric.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'sea'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Seasonal/UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Seasonal/LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Seasonal/Percentiles_parametric.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'dcp_Ann'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_Ann/TT-Analysis_UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_Ann/TT-Analysis_LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_Ann/TT-Analysis_Percentiles_parametric.nc', engine='netcdf4')
        elif (n == 'TT') & (m == 'dcp_MJJAS'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_MJJAS/TT-Analysis_UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_MJJAS/TT-Analysis_LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_MJJAS/TT-Analysis_Percentiles_parametric.nc', engine='netcdf4')
        elif (n == 'TT') & (m == 'dcp_NDJFM'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_NDJFM/TT-Analysis_UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_NDJFM/TT-Analysis_LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Decadal_NDJFM/TT-Analysis_Percentiles_parametric.nc', engine='netcdf4')
        elif (n == 'PR') & (m == 'mon'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_Precip-Monthly/UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Monthly/LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Monthly/Percentiles_parametric.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'sea'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_Precip-Seasonal/UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Seasonal/LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Seasonal/Percentiles_parametric.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'dcp_Ann'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_Ann/PR_UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_Ann/PR_LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_Ann/PR_Percentiles_parametric.nc', engine='netcdf4')
        elif (n == 'PR') & (m == 'dcp_MJJAS'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_MJJAS/PR_UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_MJJAS/PR_LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_MJJAS/PR_Percentiles_parametric.nc', engine='netcdf4')
        elif (n == 'PR') & (m == 'dcp_NDJFM'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_NDJFM/PR_UpperTercile_parametric.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_NDJFM/PR_LowerTercile_parametric.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Decadal_NDJFM/PR_Percentiles_parametric.nc', engine='netcdf4') 
    
        # Create the regridder
        regridder = xe.Regridder(
            dp_pt, dg_target, "nearest_s2d"
        ) 
        regridder
        
        #Apply the regridder
        dp_ut_out = regridder(dp_ut)
        dp_lt_out = regridder(dp_lt)
        dp_pt_out = regridder(dp_pt)

        # Save files
        if (n == 'TT') & (m == 'mon'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Monthly/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Monthly/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Monthly/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'sea'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Seasonal/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Seasonal/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Seasonal/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'dcp_Ann'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_Ann/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_Ann/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_Ann/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'dcp_MJJAS'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_MJJAS/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_MJJAS/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_MJJAS/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'dcp_NDJFM'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_NDJFM/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_NDJFM/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_AirTemp-Decadal_NDJFM/Percentiles_parametric_regridded.nc', engine='netcdf4')         
        elif (n == 'PR') & (m == 'mon'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_Precip-Monthly/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Monthly/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Monthly/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'sea'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_Precip-Seasonal/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Seasonal/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Seasonal/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'dcp_Ann'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_Ann/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_Ann/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_Ann/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'dcp_MJJAS'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_MJJAS/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_MJJAS/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_MJJAS/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'dcp_NDJFM'):
            dp_ut_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_NDJFM/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_NDJFM/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt_out.to_netcdf(data_path+'/CaSR3P2_Precip-Decadal_NDJFM/Percentiles_parametric_regridded.nc', engine='netcdf4') 