# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 09:40:19 2025

Step 4 in creating climatology files for seasonal forecasts on ClimateData.ca
Script masks the regridded data for the percentiles of the CaSR climatology, 
adds metadata, and writes the final NetCDF files for CRIM

@author: DosserH
"""

import numpy as np
import xarray as xr

# Path to grid and data
grid_path = 'path_to_grid_on_gpsc'
data_path = 'path_to_data_on_gpsc'
save_path = 'path_to_save_files_on_gpsc'

# Loop over variables: temperature 'TT' and precipitation 'PR'
# Loop over monthly 'mon' and 3-month seasonal 'sea' time periods
var_name = ['TT', 'PR'] 
period = ['mon', 'sea'] 
for i, n in enumerate(var_name):
    for j, m in enumerate(period):

        # Load the data
        if (n == 'TT') & (m == 'mon'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Monthly/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Monthly/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Monthly/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'sea'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Seasonal/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Seasonal/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_AirTemp-Seasonal/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'mon'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_Precip-Monthly/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Monthly/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Monthly/Percentiles_parametric_regridded.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'sea'):
            dp_ut = xr.open_dataset(data_path+'/CaSR3P2_Precip-Seasonal/UpperTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_lt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Seasonal/LowerTercile_parametric_regridded.nc', engine='netcdf4') 
            dp_pt = xr.open_dataset(data_path+'/CaSR3P2_Precip-Seasonal/Percentiles_parametric_regridded.nc', engine='netcdf4') 
    
        # Combine all five percentiles into a single dataset
        dp_lt["percentile"] = dp_lt[n].expand_dims("percentile")
        dp_lt["percentile"] = 0.333 #33rd percentile = lower tercile
        dp_ut["percentile"] = dp_ut[n].expand_dims("percentile")
        dp_ut["percentile"] = 0.666 #66th percentile = upper tercile
        temp_dp = xr.concat([dp_pt, dp_ut, dp_lt],dim="percentile")
        temp_dp = temp_dp.sortby("percentile")

        # Load the grid and create the mask for Canada
        dg = xr.open_dataset(grid_path+'m6_grid.nc', engine='netcdf4') 
        mask = np.squeeze(dg.isel(time=0,drop=True).pr).notnull()
        
        # Apply mask
        ds = temp_dp.where(mask, drop=True)
        
        # Adjust coordinate names
        ds = ds.assign_coords(percentile=(ds.percentile*100))
        if m == 'sea':
            ds = ds.rename({'month':'season'})           
        ds = ds.rename({'lon':'longitude'})
        ds = ds.rename({'lat':'latitude'})
            
        # Add attributes to variables 
        ds['longitude'].attrs = {
            'standard_name': 'longitude', 
            'long_name': 'longitude', 
            'units': 'degrees_east', 
            'axis': 'X'
            }
        ds['latitude'].attrs = {
            'standard_name': 'latitude', 
            'long_name': 'latitude', 
            'units': 'degrees_north', 
            'axis': 'Y'
            }
        if n == 'TT':
            ds['percentile'].attrs = {
                'long_name': 'percentiles', 
                'description_short_en': 'percentiles of the (1991-2020) CaSRv3.2 climatology calculated from a fitted normal distribution', 
                'description_short_fr': 'percentiles de la climatologie RCaSv3.2 (1991-2020) calcules a partir d’une distribution normale ajustee'
                }
        elif n == 'PR':
            ds['percentile'].attrs = {
                'long_name': 'percentiles', 
                'description_short_en': 'percentiles of the (1991-2020) CaSRv3.2 climatology calculated from a fitted gamma distribution', 
                'description_short_fr': 'percentiles de la climatologie RCaSv3.2 (1991-2020) calcules a partir d’une distribution gamma ajustee'
                }
        if m == 'mon':
            ds['month'].attrs = {
                'long_name': 'calendar months / mois de l’annee', 
                'description_short_en': 'months of the year (e.g., 1=Jan)', 
                'description_short_fr': 'mois de l’annee (p. ex., 1 = janv.)', 
                'axis': 'T'
                }
            if n == 'TT':
                ds['TT'].attrs = {
                    'long_name': 'air temperature (1.5m) / temperature de l’air (1,5m)', 
                    'description_short_en': 'percentiles of monthly-mean 1.5m air temperature', 
                    'description_short_fr': 'percentiles de la temperature moyenne mensuelle de l’air a 1,5m', 
                    'units': 'C'
                    }
            elif n == 'PR':
                ds['PR'].attrs = {
                    'long_name': 'quantity of precipitation / quantite de precipitations', 
                    'description_short_en': 'percentiles of monthly-mean quantity of precipitation accumulated in mm per day', 
                    'description_short_fr': 'percentiles de la quantite moyenne mensuelle de precipitations accumulees en mm par jour', 
                    'units': 'mm', 
                    'accumulation_period': '1D'
                    }
        elif m == 'sea':
            ds['season'].attrs = {
                'long_name': '3-month seasons / saisons de trois mois', 
                'description_short_en': '3-month rolling seasons (e.g., 1=JFM)', 
                'description_short_fr': 'saisons mobiles de trois mois (p. ex., 1 = jfm)', 
                'axis': 'T'
                }
            if n == 'TT':
                ds['TT'].attrs = {
                    'long_name': 'air temperature (1.5m) / temperature de l’air (1,5m)', 
                    'description_short_en': 'percentiles of seasonal-mean 1.5m air temperature', 
                    'description_short_fr': 'percentiles de la temperature moyenne saisonniere de l’air a 1,5m', 
                    'units': 'C'
                    }
            elif n == 'PR':
                ds['PR'].attrs = {
                    'long_name': 'quantity of precipitation / quantite de precipitations', 
                    'description_short_en': 'percentiles of seasonal-mean quantity of precipitation accumulated in mm per day', 
                    'description_short_fr': 'percentiles de la quantite moyenne saisonniere de precipitations accumulees en mm par jour', 
                    'units': 'mm', 
                    'accumulation_period': '1D'
                    }

        # Add global attributes
        ds.attrs = {
            'Conventions': 'CF-1.6', 
            'institution': 'Environment and Climate Change Canada / Environnement et Changement climatique Canada',
            'title': 'Percentiles of the CaSRv3.2 1991-2020 climatology, re-gridded to a 1/12th of a degree latitude-longitude grid for a Canada-wide domain / Percentiles de la climatologie RCaSv3.2 pour 1991-2020, redimensionnes sur une grille latitude-longitude de 1/12e de degre sur un domaine pancanadien', 
            'history': '16/02/2026 : File created using CaSRv3.2 data accessed Jan 21 2026 / Fichier cree a partir des donnees RCaSv3.2 consultees le 21 janvier 2026', 
            'contact': 'ccsc-cccs@ec.gc.ca', 
            'CaSR_source': 'https://hpfx.collab.science.gc.ca/~scar700/rcas-casr/', 
            'CaSR_institution': 'Environment and Climate Change Canada / Environnement et Changement climatique Canada', 
            'CaSR_title': 'Canadian Surface Reanalysis (CaSR) / Reanalyse Canadienne de Surface (RCaS)', 
            'CaSR_contact' : 'rcas-casr@ec.gc.ca', 
            'licence': 'These data are produced and provided by Environment and Climate Change Canada. License agreement can be found at https://open.canada.ca/en/open-government-licence-canada / Ces donnees sont produites et fournies par Environnement et Changement climatique Canada. Le contrat de license peut etre trouve dans https://ouvert.canada.ca/fr/licence-du-gouvernement-ouvert-canada'
            }

        # Save files
        if (n == 'TT') & (m == 'mon'):
            ds.to_netcdf(save_path+'/mth_pctl_CaSRv3.2_1991-2020_AirTemp.nc', engine='netcdf4') 
        elif (n == 'TT') & (m == 'sea'):
            ds.to_netcdf(save_path+'/sea_pctl_CaSRv3.2_1991-2020_AirTemp.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'mon'):
            ds.to_netcdf(save_path+'/mth_pctl_CaSRv3.2_1991-2020_PrecipAccum.nc', engine='netcdf4') 
        elif (n == 'PR') & (m == 'sea'):
            ds.to_netcdf(save_path+'/sea_pctl_CaSRv3.2_1991-2020_PrecipAccum.nc', engine='netcdf4') 
