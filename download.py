import pandas as pd
import numpy as np


cost_df = pd.read_csv("modifiedCost.csv")
cost_df = cost_df[cost_df['SDA'].notna()]
cost_df = cost_df.rename(columns={'SDA':'region','type':'category','post':'post-cost','meas':'measurement','treat':'treatment','sfy':'state-fiscal-yr',
                                'rgrp3':'child', 'rgrp4': 'blind/disabled','rgrp6':'telemonitoring','tot_tvst':'total-televisits'})
cost_df['other-televisits'] = cost_df['total-televisits']-cost_df['blind/disabled']-cost_df['child']           
cost_df = cost_df[['region','category','post-cost','measurement','treatment','state-fiscal-yr','blind/disabled','child','other-televisits','total-televisits','telemonitoring']]                     

demo_df = pd.read_csv('modifiedDemo.csv')
demo_df = demo_df[demo_df['SDA'].notna()]

demo_df = demo_df.rename(columns={'SDA':'region','demo':'pat-char','sfy':'state-fiscal-yr','rgrp31':'Child-Treat', 'rgrp32':'Child-Comp',  'rgrp41': 'Blind/Disabled-Treat', 'rgrp42':'Blind/Disabled-Comp',
                                'rgrp61':'Telemonitoring-Treat','rgrp62':'Telemonitoring-Comp'})
demo_df = demo_df.drop(['ord'],axis=1)

inpatcost_df = pd.read_csv("sda_smmry.csv")
inpatcost_df = inpatcost_df.rename(columns={'SDA':'region','ccsr':'category','calendar-yr':'year','n_hospitalizations':'inpatient_ct'})
inpatcost_df = inpatcost_df.drop(['uci_los','lci_los','lci_chrg','uci_chrg','Obs'],axis=1)

inpatcost_df.to_excel("doc/inpatient-costs-data.xlsx",index=False)

with pd.ExcelWriter('doc/cost-study-data.xlsx') as writer:
    demo_df.to_excel(writer,sheet_name='demographics',index=False)
    cost_df.to_excel(writer,sheet_name='costs',index=False)
    
