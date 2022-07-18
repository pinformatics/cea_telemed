#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 09:47:19 2022

@author: margaretblack
"""
import os
os.chdir('/Users/margaretblack/OneDrive - Texas A&M University/X-Grant Documents/aim2/mblack')
import pandas as pd
from lib import demo_clean, cost_clean

fn = './data/cntrl_mcost_fltrd.csv'

df = pd.read_csv(fn)
byvar = 'Number of Clients' 
currency_vars = ['Total, Before Pre-Period',
       'Serious, Before Pre-Period', 'Other, Before Pre-Period',
       'Total, Pre-Period', 'Serious, Pre-Period', 'Other, Pre-Period',
       'Total, Index Period', 'Serious, Index Period', 'Other, Index Period',
       'Total, Post-Period', 'Serious, Post-Period', 'Other, Post-Period',
       'Total, After Post-Period', 'Serious, After Post-Period',
       'Other, After Post-Period']
nan_idx = df[byvar].isna()
replace_nan = df[nan_idx].fillna('---')
non_nan = df[~nan_idx]

non_nan[byvar] = non_nan[byvar].map('{:,.2f}'.format)
for col in currency_vars:
    non_nan[col] = non_nan[col].map('${:,.2f}'.format)
df_final = pd.concat([replace_nan, non_nan], axis=0)

mace_types = ['Total', 'Serious', 'Other']
macey_type = mace_types[0]
[currency_vars.index(var) for var in currency_vars if mace_type in var.split(', ')[0]]


df_treat = demo_clean.clean('./data/tmon_demo_fltrd.csv')
df_comp = demo_clean.clean('./data/cntrl_demo_fltrd.csv')

byvar = 'SDA'
default_item = 'Texas'
menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
             'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
selected_item = 'Texas' #request.form.get('menu_items')
menu_items_new = [selected_item] + [item for item in menu_items if item != selected_item]
selected_item_idx = df_treat[byvar] == selected_item
df_treat[selected_item_idx].drop(columns=['SDA'])
