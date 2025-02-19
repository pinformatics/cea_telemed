from flask import Flask, render_template, request, redirect, send_file
import requests
import json
import pandas as pd
import numpy as np

from lib.demo_clean import demo_subset
from lib.cost_clean import cost_subset

pd.options.mode.chained_assignment = None  # default='warn'
app = Flask(__name__)

url = "./data/modifiedCost.csv" #Values replaced with less than or equal to 5 with np.nan
sda = []

df = pd.read_csv(url,error_bad_lines=False)

df = df.rename(columns={'rgrp3':'Child', 'rgrp4': 'Blind/Disabled','rgrp6':'Telemonitoring','sfy':'Year','SDA' : 'Region','tot_tvst':'Televisits'})
df = df.fillna(0)

df['Other'] = df['Televisits']-df['Blind/Disabled']-df['Child']
df = df[["Region","Year","Blind/Disabled","Child","Other","Televisits","Telemonitoring","treat","meas","type","post"]]

sda = (df['Region'].unique())
sda = np.roll(sda,2)
sda = sda[sda!=0]
sda = [x for x in sda if pd.isnull(x) == False]


nclients = df[df['meas']=='nclient']
#nclients.loc[nclients['Telemonitoring'] <= 5.0 , ['Telemonitoring']] = np.nan


#----------------------------------------------------Medical Cost------------------------------------------#
med_df = df[df['type']=='med']

#pre cost
med_df_precost = med_df[med_df['post']==0]
#post cost
med_df_postcost = med_df[med_df['post']==1]

texas_nclient = nclients[nclients['Region']=='Texas']
texas_nclient=texas_nclient.drop(['type','post','meas'],axis=1)
texas_nclient = texas_nclient.sort_values(by=['treat'])

texas_nclient['Child'] = texas_nclient['Child'].map('{:,.0f}'.format)
texas_nclient['Blind/Disabled'] = texas_nclient['Blind/Disabled'].map('{:,.0f}'.format)
texas_nclient['Telemonitoring'] = texas_nclient['Telemonitoring'].map('{:,.0f}'.format)
texas_nclient['Televisits'] = texas_nclient['Televisits'].map('{:,.0f}'.format)
texas_nclient['Other'] = texas_nclient['Other'].map('{:,.0f}'.format)
#texas_nclient = texas_nclient.rename(columns={'Telemonitoring':'Total ','Televisits':'Total'})
texas_nclient_tele = texas_nclient[texas_nclient['treat']==1]
texas_nclient_nontele = texas_nclient[texas_nclient['treat']==0]
texas_nclient_tele=texas_nclient_tele.drop(['treat','Region'],axis=1)
texas_nclient_nontele=texas_nclient_nontele.drop(['treat','Region','Year'],axis=1)
texas_nclient_nontele = texas_nclient_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_nclient_tele.reset_index(drop=True,inplace=True)
texas_nclient_nontele.reset_index(drop=True, inplace=True)
texas_numclient = pd.concat([texas_nclient_tele,texas_nclient_nontele],axis=1)

texas_numclient = texas_numclient[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_numclient = texas_numclient.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
texas_numclient = texas_numclient.replace(to_replace = "0", value ="---")      

texas_precost = med_df_precost[med_df_precost['Region']=='Texas']
texas_precost=texas_precost.drop(['type','post','meas'],axis=1)
texas_precost['Blind/Disabled'] = texas_precost['Blind/Disabled'].apply(np.round)
texas_precost['Child'] = texas_precost['Child'].apply(np.round)
texas_precost['Telemonitoring'] = texas_precost['Telemonitoring'].apply(np.round)
texas_precost['Other'] = texas_precost['Other'].apply(np.round)
texas_precost = texas_precost.sort_values(by=['treat'])
texas_precost['Child'] = texas_precost['Child'].map('${:,.0f}'.format)
texas_precost['Blind/Disabled'] = texas_precost['Blind/Disabled'].map('${:,.0f}'.format)
texas_precost['Telemonitoring'] = texas_precost['Telemonitoring'].map('${:,.0f}'.format)
texas_precost['Televisits'] = texas_precost['Televisits'].map('${:,.0f}'.format)
texas_precost['Other'] = texas_precost['Other'].map('${:,.0f}'.format)
#texas_precost = texas_precost.rename(columns={'Telemonitoring':'Total ','Televisits':'Total'})
texas_precost_tele = texas_precost[texas_precost['treat']==1]
texas_precost_nontele = texas_precost[texas_precost['treat']==0]
texas_precost_tele=texas_precost_tele.drop(['treat','Region'],axis=1)
texas_precost_nontele=texas_precost_nontele.drop(['treat','Region','Year'],axis=1)
texas_precost_nontele = texas_precost_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_precost_tele.reset_index(drop=True,inplace=True)
texas_precost_nontele.reset_index(drop=True, inplace=True)
texas_precost_final = pd.concat([texas_precost_tele,texas_precost_nontele],axis=1)
texas_precost_final = texas_precost_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_precost_final = texas_precost_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
texas_precost_final = texas_precost_final.replace(to_replace = "$0", value ="---")                                                              
texas_precost_final = texas_precost_final.replace(to_replace = "$-0", value ="---")                                                              

texas_postcost = med_df_postcost[med_df_postcost['Region']=='Texas']
texas_postcost=texas_postcost.drop(['type','post','meas'],axis=1)
texas_postcost['Blind/Disabled'] = texas_postcost['Blind/Disabled'].apply(np.round)
texas_postcost['Child'] = texas_postcost['Child'].apply(np.round)
texas_postcost['Telemonitoring'] = texas_postcost['Telemonitoring'].apply(np.round)
texas_postcost['Other'] = texas_postcost['Other'].apply(np.round)
texas_postcost = texas_postcost.sort_values(by=['treat'])
texas_postcost['Child'] = texas_postcost['Child'].map('${:,.0f}'.format)
texas_postcost['Blind/Disabled'] = texas_postcost['Blind/Disabled'].map('${:,.0f}'.format)
texas_postcost['Telemonitoring'] = texas_postcost['Telemonitoring'].map('${:,.0f}'.format) 
texas_postcost['Televisits'] = texas_postcost['Televisits'].map('${:,.0f}'.format)
texas_postcost['Other'] = texas_postcost['Other'].map('${:,.0f}'.format)
#texas_postcost = texas_postcost.rename(columns={'Telemonitoring':'Total ','Televisits':'Total'})
texas_postcost_tele = texas_postcost[texas_postcost['treat']==1]
texas_postcost_nontele = texas_postcost[texas_postcost['treat']==0]
texas_postcost_tele=texas_postcost_tele.drop(['treat','Region'],axis=1)
texas_postcost_nontele=texas_postcost_nontele.drop(['treat','Region','Year'],axis=1)
texas_postcost_nontele = texas_postcost_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_postcost_tele.reset_index(drop=True,inplace=True)
texas_postcost_nontele.reset_index(drop=True, inplace=True)
texas_postcost_final = pd.concat([texas_postcost_tele,texas_postcost_nontele],axis=1)     
texas_postcost_final = texas_postcost_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_postcost_final = texas_postcost_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})       
texas_postcost_final = texas_postcost_final.replace(to_replace = "$0", value ="---")      
texas_postcost_final = texas_postcost_final.replace(to_replace = "$-0", value ="---")                                                  


#----------------------------------------------------Inpatient Cost------------------------------------------#
inpat_df = df[df['type']=='inp']

#pre cost
inpat_df_precost = inpat_df[inpat_df['post']==0]
inpat_df_precost = inpat_df_precost[inpat_df_precost['meas']=='cost']
#post cost
inpat_df_postcost = inpat_df[inpat_df['post']==1]
inpat_df_postcost = inpat_df_postcost[inpat_df_postcost['meas']=='cost']

inpat_encount = inpat_df[inpat_df['meas']=='cnt']

texas_postcost_inpat = inpat_df_postcost[inpat_df_postcost['Region']=='Texas']
texas_postcost_inpat = texas_postcost_inpat.drop(['type','post','meas'],axis=1)
texas_postcost_inpat['Blind/Disabled'] = texas_postcost_inpat['Blind/Disabled'].apply(np.round)
texas_postcost_inpat['Child'] = texas_postcost_inpat['Child'].apply(np.round)
texas_postcost_inpat['Telemonitoring'] = texas_postcost_inpat['Telemonitoring'].apply(np.round)
texas_postcost_inpat['Other'] = texas_postcost_inpat['Other'].apply(np.round)
texas_postcost_inpat = texas_postcost_inpat.sort_values(by=['treat'])
texas_postcost_inpat['Child'] = texas_postcost_inpat['Child'].map('${:,.0f}'.format)
texas_postcost_inpat['Blind/Disabled'] = texas_postcost_inpat['Blind/Disabled'].map('${:,.0f}'.format)
texas_postcost_inpat['Telemonitoring'] = texas_postcost_inpat['Telemonitoring'].map('${:,.0f}'.format) 
texas_postcost_inpat['Televisits'] = texas_postcost_inpat['Televisits'].map('${:,.0f}'.format)
texas_postcost_inpat['Other'] = texas_postcost_inpat['Other'].map('${:,.0f}'.format)
#texas_postcost_inpat = texas_postcost_inpat.rename(columns={'Telemonitoring':'Total ','Televisits':'Total'})
texas_postcost_tele_inpat = texas_postcost_inpat[texas_postcost_inpat['treat']==1]
texas_postcost_nontele_inpat = texas_postcost_inpat[texas_postcost_inpat['treat']==0]
texas_postcost_tele_inpat=texas_postcost_tele_inpat.drop(['treat','Region'],axis=1)
texas_postcost_nontele_inpat=texas_postcost_nontele_inpat.drop(['treat','Region','Year'],axis=1)
texas_postcost_nontele_inpat = texas_postcost_nontele_inpat.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_postcost_tele_inpat.reset_index(drop=True,inplace=True)
texas_postcost_nontele_inpat.reset_index(drop=True, inplace=True)
texas_postcost_inpat_final = pd.concat([texas_postcost_tele_inpat,texas_postcost_nontele_inpat],axis=1)     
texas_postcost_inpat_final = texas_postcost_inpat_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_postcost_inpat_final = texas_postcost_inpat_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'}) 
texas_postcost_inpat_final = texas_postcost_inpat_final.replace(to_replace = "$0", value ="---")                                                                 
texas_postcost_inpat_final = texas_postcost_inpat_final.replace(to_replace = "$-0", value ="---")                                                                 


texas_inpat_encount_df = inpat_encount[inpat_encount['Region']=='Texas']
texas_inpat_encount_df = texas_inpat_encount_df.sort_values(by=['treat'])
texas_inpat_encount_df= texas_inpat_encount_df.drop(['type','post','meas'],axis=1)                      
texas_inpat_encount_df['Child'] = texas_inpat_encount_df['Child'].map('{:,.3f}'.format)
texas_inpat_encount_df['Blind/Disabled'] = texas_inpat_encount_df['Blind/Disabled'].map('{:,.3f}'.format)
texas_inpat_encount_df['Telemonitoring'] = texas_inpat_encount_df['Telemonitoring'].map('{:,.3f}'.format)
texas_inpat_encount_df['Televisits'] = texas_inpat_encount_df['Televisits'].map('{:,.3f}'.format)
texas_inpat_encount_df['Other'] = texas_inpat_encount_df['Other'].map('{:,.3f}'.format)        
#texas_inpat_encount_df = texas_inpat_encount_df.rename(columns={'Telemonitoring':'Total','Televisits':'Total'})
texas_inpat_encount_tele = texas_inpat_encount_df[texas_inpat_encount_df['treat']==1]
texas_inpat_encount_nontele = texas_inpat_encount_df[texas_inpat_encount_df['treat']==0]
texas_inpat_encount_tele=texas_inpat_encount_tele.drop(['treat','Region'],axis=1)
texas_inpat_encount_nontele = texas_inpat_encount_nontele.drop(['treat','Region','Year'],axis=1)
texas_inpat_encount_nontele = texas_inpat_encount_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})

texas_inpat_encount_tele.reset_index(drop=True,inplace=True)
texas_inpat_encount_nontele.reset_index(drop=True, inplace=True)       
texas_inpat_encount_final = pd.concat([texas_inpat_encount_tele,texas_inpat_encount_nontele],axis=1)     
texas_inpat_encount_final = texas_inpat_encount_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_inpat_encount_final = texas_inpat_encount_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})   
texas_inpat_encount_final = texas_inpat_encount_final.replace(to_replace = "0.000", value ="---")                                                                      
texas_inpat_encount_final = texas_inpat_encount_final.replace(to_replace = "-0.000", value ="---")                                                                      
                                                          
#----------------------------------------------------ED Cost------------------------------------------#
ed_df = df[df['type']=='ed']

#pre cost
ed_df_precost = ed_df[ed_df['post']==0]
ed_df_precost = ed_df_precost[ed_df_precost['meas']=='cost']
#post cost
ed_df_postcost = ed_df[ed_df['post']==1]
ed_df_postcost = ed_df_postcost[ed_df_postcost['meas']=='cost']

ed_visits = ed_df[ed_df['meas']=='cnt']


texas_postcost_ed = ed_df_postcost[ed_df_postcost['Region']=='Texas']
texas_postcost_ed = texas_postcost_ed.drop(['type','post','meas'],axis=1)
texas_postcost_ed['Blind/Disabled'] = texas_postcost_ed['Blind/Disabled'].apply(np.round)
texas_postcost_ed['Child'] = texas_postcost_ed['Child'].apply(np.round)
texas_postcost_ed['Telemonitoring'] = texas_postcost_ed['Telemonitoring'].apply(np.round)
texas_postcost_ed['Other'] = texas_postcost_ed['Other'].apply(np.round)
texas_postcost_ed = texas_postcost_ed.sort_values(by=['treat'])
texas_postcost_ed['Child'] = texas_postcost_ed['Child'].map('${:,.0f}'.format)
texas_postcost_ed['Blind/Disabled'] = texas_postcost_ed['Blind/Disabled'].map('${:,.0f}'.format)
texas_postcost_ed['Telemonitoring'] = texas_postcost_ed['Telemonitoring'].map('${:,.0f}'.format) 
texas_postcost_ed['Televisits'] = texas_postcost_ed['Televisits'].map('${:,.0f}'.format)
texas_postcost_ed['Other'] = texas_postcost_ed['Other'].map('${:,.0f}'.format)
#texas_postcost_ed = texas_postcost_ed.rename(columns={'Telemonitoring':'Total ','Televisits':'Total'})
texas_postcost_tele_ed = texas_postcost_ed[texas_postcost_ed['treat']==1]
texas_postcost_nontele_ed = texas_postcost_ed[texas_postcost_ed['treat']==0]
texas_postcost_tele_ed=texas_postcost_tele_ed.drop(['treat','Region'],axis=1)
texas_postcost_nontele_ed=texas_postcost_nontele_ed.drop(['treat','Region','Year'],axis=1)
texas_postcost_nontele_ed = texas_postcost_nontele_ed.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_postcost_tele_ed.reset_index(drop=True,inplace=True)
texas_postcost_nontele_ed.reset_index(drop=True, inplace=True)
texas_postcost_ed_final = pd.concat([texas_postcost_tele_ed,texas_postcost_nontele_ed],axis=1)     
texas_postcost_ed_final = texas_postcost_ed_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_postcost_ed_final = texas_postcost_ed_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})     
texas_postcost_ed_final = texas_postcost_ed_final.replace(to_replace = "$0", value ="---")              
texas_postcost_ed_final = texas_postcost_ed_final.replace(to_replace = "$-0", value ="---")              

texas_ed_visits_df = ed_visits[ed_visits['Region']=='Texas']
texas_ed_visits_df = texas_ed_visits_df.sort_values(by=['treat'])
texas_ed_visits_df= texas_ed_visits_df.drop(['type','post','meas'],axis=1)                      
texas_ed_visits_df['Child'] = texas_ed_visits_df['Child'].map('{:,.3f}'.format)
texas_ed_visits_df['Blind/Disabled'] = texas_ed_visits_df['Blind/Disabled'].map('{:,.3f}'.format)
texas_ed_visits_df['Telemonitoring'] = texas_ed_visits_df['Telemonitoring'].map('{:,.3f}'.format)
texas_ed_visits_df['Televisits'] = texas_ed_visits_df['Televisits'].map('{:,.3f}'.format)
texas_ed_visits_df['Other'] = texas_ed_visits_df['Other'].map('{:,.3f}'.format)        
#texas_ed_visits_df = texas_ed_visits_df.rename(columns={'Telemonitoring':'Total','Televisits':'Total'})
texas_ed_visits_tele = texas_ed_visits_df[texas_ed_visits_df['treat']==1]
texas_ed_visits_nontele = texas_ed_visits_df[texas_ed_visits_df['treat']==0]
texas_ed_visits_tele=texas_ed_visits_tele.drop(['treat','Region'],axis=1)
texas_ed_visits_nontele=texas_ed_visits_nontele.drop(['treat','Region','Year'],axis=1)

texas_ed_visits_nontele = texas_ed_visits_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_ed_visits_tele.reset_index(drop=True,inplace=True)
texas_ed_visits_nontele.reset_index(drop=True, inplace=True)
texas_ed_visits_final = pd.concat([texas_ed_visits_tele,texas_ed_visits_nontele],axis=1)     
texas_ed_visits_final = texas_ed_visits_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_ed_visits_final = texas_ed_visits_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})     
texas_ed_visits_final = texas_ed_visits_final.replace(to_replace = "0.000", value ="---")              
texas_ed_visits_final = texas_ed_visits_final.replace(to_replace = "-0.000", value ="---")              


#----------------------------------------------------Outpatient Cost------------------------------------------#
outpat_df = df[df['type']=='out']

#pre cost
outpat_df_precost = outpat_df[outpat_df['post']==0]
outpat_df_precost = outpat_df_precost[outpat_df_precost['meas']=='cost']
#post cost
outpat_df_postcost = outpat_df[outpat_df['post']==1]
outpat_df_postcost = outpat_df_postcost[outpat_df_postcost['meas']=='cost']
outpat_visits = outpat_df[outpat_df['meas']=='cnt']

texas_postcost_outpat = outpat_df_postcost[outpat_df_postcost['Region']=='Texas']
texas_postcost_outpat = texas_postcost_outpat.drop(['type','post','meas'],axis=1)
texas_postcost_outpat['Blind/Disabled'] = texas_postcost_outpat['Blind/Disabled'].apply(np.round)
texas_postcost_outpat['Child'] = texas_postcost_outpat['Child'].apply(np.round)
texas_postcost_outpat['Telemonitoring'] = texas_postcost_outpat['Telemonitoring'].apply(np.round)
texas_postcost_outpat['Other'] = texas_postcost_outpat['Other'].apply(np.round)
texas_postcost_outpat = texas_postcost_outpat.sort_values(by=['treat'])
texas_postcost_outpat['Child'] = texas_postcost_outpat['Child'].map('${:,.0f}'.format)
texas_postcost_outpat['Blind/Disabled'] = texas_postcost_outpat['Blind/Disabled'].map('${:,.0f}'.format)
texas_postcost_outpat['Telemonitoring'] = texas_postcost_outpat['Telemonitoring'].map('${:,.0f}'.format) 
texas_postcost_outpat['Televisits'] = texas_postcost_outpat['Televisits'].map('${:,.0f}'.format)
texas_postcost_outpat['Other'] = texas_postcost_outpat['Other'].map('${:,.0f}'.format)
#texas_postcost_outpat = texas_postcost_outpat.rename(columns={'Telemonitoring':'Total ','Televisits':'Total'})
texas_postcost_tele_outpat = texas_postcost_outpat[texas_postcost_outpat['treat']==1]
texas_postcost_nontele_outpat = texas_postcost_outpat[texas_postcost_outpat['treat']==0]
texas_postcost_tele_outpat=texas_postcost_tele_outpat.drop(['treat','Region'],axis=1)
texas_postcost_nontele_outpat=texas_postcost_nontele_outpat.drop(['treat','Region','Year'],axis=1)
texas_postcost_nontele_outpat = texas_postcost_nontele_outpat.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_postcost_tele_outpat.reset_index(drop=True,inplace=True)
texas_postcost_nontele_outpat.reset_index(drop=True, inplace=True)
texas_postcost_outpat_final = pd.concat([texas_postcost_tele_ed,texas_postcost_nontele_ed],axis=1)     
texas_postcost_outpat_final = texas_postcost_outpat_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_postcost_outpat_final = texas_postcost_outpat_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})     
texas_postcost_outpat_final = texas_postcost_outpat_final.replace(to_replace = "$0", value ="---")              
texas_postcost_outpat_final = texas_postcost_outpat_final.replace(to_replace = "$-0", value ="---")             

texas_outpat_visits_df = outpat_visits[outpat_visits['Region']=='Texas']
texas_outpat_visits_df = texas_outpat_visits_df.sort_values(by=['treat'])
texas_outpat_visits_df= texas_outpat_visits_df.drop(['type','post','meas'],axis=1)                      
texas_outpat_visits_df['Child'] = texas_outpat_visits_df['Child'].map('{:,.3f}'.format)
texas_outpat_visits_df['Blind/Disabled'] = texas_outpat_visits_df['Blind/Disabled'].map('{:,.3f}'.format)
texas_outpat_visits_df['Telemonitoring'] = texas_outpat_visits_df['Telemonitoring'].map('{:,.3f}'.format)
texas_outpat_visits_df['Televisits'] = texas_outpat_visits_df['Televisits'].map('{:,.3f}'.format)
texas_outpat_visits_df['Other'] = texas_outpat_visits_df['Other'].map('{:,.3f}'.format)        
#texas_outpat_visits_df = texas_outpat_visits_df.rename(columns={'Telemonitoring':'Total','Televisits':'Total'})
texas_outpat_visits_tele = texas_outpat_visits_df[texas_outpat_visits_df['treat']==1]
texas_outpat_visits_nontele = texas_outpat_visits_df[texas_outpat_visits_df['treat']==0]
texas_outpat_visits_tele=texas_outpat_visits_tele.drop(['treat','Region'],axis=1)
texas_outpat_visits_nontele=texas_outpat_visits_nontele.drop(['treat','Region','Year'],axis=1)
texas_outpat_visits_nontele = texas_outpat_visits_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
texas_outpat_visits_tele.reset_index(drop=True,inplace=True)
texas_outpat_visits_nontele.reset_index(drop=True, inplace=True)
texas_outpat_visits_final = pd.concat([texas_outpat_visits_tele,texas_outpat_visits_nontele],axis=1)     
texas_outpat_visits_final = texas_outpat_visits_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
texas_outpat_visits_final = texas_outpat_visits_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                        'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})     

texas_outpat_visits_final = texas_outpat_visits_final.replace(to_replace = "0.000", value ="---")              
texas_outpat_visits_final = texas_outpat_visits_final.replace(to_replace = "-0.000", value ="---")              

@app.route('/', methods=["GET","POST"])
@app.route('/home',methods=["GET","POST"])
def home():
    return render_template("home.html")

@app.route('/download_cea')
def download_file():
    path = "doc/CEA-basic-tool-v16.xlsx"
    return send_file(path,as_attachment=True)

@app.route('/download_cost_study')
def download_excel():
    path = "doc/cost-study-data.xlsx"
    return send_file(path,as_attachment=True)

@app.route('/download_inpatcost')
def download_excel1():
    path = "doc/inpatient-costs-data.xlsx"
    return send_file(path,as_attachment=True)

@app.route('/download_ceatool')
def download_ceatool():
    path = "doc/CEA-Tool-TAMU.pdf"
    return send_file(path,as_attachment=True)

''' start marg additions 
'''
@app.route('/download_tmon_demo')
def download_tmon_demo():
    path = './data/tmon_cntrl_demo.csv'
    return send_file(path,as_attachment=True)
@app.route('/download_tmon_costs')
def download_tmon_costs():
    path = './data/tmon_cntrl_costs.csv'
    return send_file(path,as_attachment=True)
@app.route('/download_tmon_hptn_demo')
def download_tmon_hptn_demo():
    path = './data/tmon_cntrl_demo_hptn.csv'
    return send_file(path,as_attachment=True)
@app.route('/download_tmon_hptn_costs')
def download_tmon_hptn_costs():
    path = './data/tmon_cntrl_costs_hptn.csv'
    return send_file(path,as_attachment=True)
''' end marg additions
'''
@app.route('/medcost', methods=["GET", "POST"])
def medcost():
    if request.method == "POST":
        sda_name = request.form.get("sda", None)
        num_client = nclients[nclients['Region']==sda_name]
        num_client = num_client.sort_values(by=['treat'])
        num_client=num_client.drop(['type','post','meas'],axis=1)        
        num_client['Child'] = num_client['Child'].map('{:,.0f}'.format)
        num_client['Blind/Disabled'] = num_client['Blind/Disabled'].map('{:,.0f}'.format)        
        num_client['Telemonitoring'] = num_client['Telemonitoring'].map('{:,.0f}'.format)
        num_client['Televisits'] = num_client['Televisits'].map('{:,.0f}'.format)
        num_client['Other'] = num_client['Other'].map('{:,.0f}'.format)
        num_client['Telemonitoring'] = num_client['Telemonitoring'].astype(str)                             
        numclient_tele = num_client[num_client['treat']==1]
        numclient_nontele = num_client[num_client['treat']==0]
        numclient_tele=numclient_tele.drop(['treat','Region'],axis=1)
        numclient_nontele=numclient_nontele.drop(['treat','Region','Year'],axis=1)
        numclient_nontele = numclient_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        numclient_tele.reset_index(drop=True,inplace=True)
        numclient_nontele.reset_index(drop=True, inplace=True)
        numclient_final = pd.concat([numclient_tele,numclient_nontele],axis=1)
        numclient_final = numclient_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        numclient_final = numclient_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        
        numclient_final = numclient_final.replace(to_replace = "0", value ="---")        

        df_precost = med_df_precost[med_df_precost['Region']==sda_name]
        df_precost = df_precost.sort_values(by=['treat'])
        df_precost=df_precost.drop(['type','post','meas'],axis=1)
        df_precost['Blind/Disabled'] = df_precost['Blind/Disabled'].apply(np.round)
        df_precost['Child'] = df_precost['Child'].apply(np.round)
        df_precost['Telemonitoring'] = df_precost['Telemonitoring'].apply(np.round)
        df_precost['Other'] = df_precost['Other'].apply(np.round)
        df_precost['Child'] = df_precost['Child'].map('${:,.0f}'.format)
        df_precost['Blind/Disabled'] = df_precost['Blind/Disabled'].map('${:,.0f}'.format)
        df_precost['Telemonitoring'] = df_precost['Telemonitoring'].map('${:,.0f}'.format)
        df_precost['Televisits'] = df_precost['Televisits'].map('${:,.0f}'.format)
        df_precost['Other'] = df_precost['Other'].map('${:,.0f}'.format)
        #df_precost = df_precost.rename(columns={'Telemonitoring':'Total','Televisits':'Total'})
        precost_tele = df_precost[df_precost['treat']==1]
        precost_nontele = df_precost[df_precost['treat']==0]
        precost_tele=precost_tele.drop(['treat','Region'],axis=1)
        precost_nontele=precost_nontele.drop(['treat','Region','Year'],axis=1)
        precost_nontele = precost_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        precost_tele.reset_index(drop=True,inplace=True)
        precost_nontele.reset_index(drop=True, inplace=True)
        precost_final = pd.concat([precost_tele,precost_nontele],axis=1)
        precost_final = precost_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        precost_final = precost_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        precost_final = precost_final.replace(to_replace = "$0", value ="---")    
        precost_final = precost_final.replace(to_replace = "$-0", value ="---")                                                               


        df_postcost = med_df_postcost[med_df_postcost['Region']==sda_name]
        df_postcost = df_postcost.sort_values(by=['treat'])
        df_postcost=df_postcost.drop(['type','post','meas'],axis=1)
        df_postcost['Blind/Disabled'] = df_postcost['Blind/Disabled'].apply(np.round)
        df_postcost['Child'] = df_postcost['Child'].apply(np.round)  
        df_postcost['Telemonitoring'] = df_postcost['Telemonitoring'].apply(np.round)   
        df_postcost['Other'] = df_postcost['Other'].apply(np.round)   
        df_postcost['Child'] = df_postcost['Child'].map('${:,.0f}'.format)
        df_postcost['Blind/Disabled'] = df_postcost['Blind/Disabled'].map('${:,.0f}'.format)
        df_postcost['Telemonitoring'] = df_postcost['Telemonitoring'].map('${:,.0f}'.format)     
        df_postcost['Televisits'] = df_postcost['Televisits'].map('${:,.0f}'.format)
        df_postcost['Other'] = df_postcost['Other'].map('${:,.0f}'.format)
        postcost_tele = df_postcost[df_postcost['treat']==1]
        postcost_nontele = df_postcost[df_postcost['treat']==0]
        postcost_tele=postcost_tele.drop(['treat','Region'],axis=1)
        postcost_nontele=postcost_nontele.drop(['treat','Region','Year'],axis=1)
        postcost_nontele = postcost_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        postcost_tele.reset_index(drop=True,inplace=True)
        postcost_nontele.reset_index(drop=True, inplace=True)
        postcost_final = pd.concat([postcost_tele,postcost_nontele],axis=1)
        postcost_final = postcost_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        postcost_final = postcost_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        postcost_final = postcost_final.replace(to_replace = "$0", value ="---") 
        postcost_final = postcost_final.replace(to_replace = "$-0", value ="---")                                                               
        if sda_name != None:
            return render_template("medcost.html", sda_name=sda_name, sda=sda, numclient_final=[numclient_final.to_html(index = False)],
                                    precost_final=[precost_final.to_html(index = False)], postcost_final=[postcost_final.to_html(index = False)])
    
    return render_template('medcost1.html',sda=sda, texas_numclient=[texas_numclient.to_html(index=False)], texas_precost_final=[texas_precost_final.to_html(index=False)], 
                            texas_postcost_final=[texas_postcost_final.to_html(index = False)])
    
    
@app.route('/inpatcost', methods=["GET", "POST"])
def inpatcost():
    if request.method == "POST":
        sda_name = request.form.get("sda", None)
        num_client = nclients[nclients['Region']==sda_name]
        num_client = num_client.sort_values(by=['treat'])
        num_client=num_client.drop(['type','post','meas'],axis=1)        
        num_client['Child'] = num_client['Child'].map('{:,.0f}'.format)
        num_client['Blind/Disabled'] = num_client['Blind/Disabled'].map('{:,.0f}'.format)        
        num_client['Telemonitoring'] = num_client['Telemonitoring'].map('{:,.0f}'.format)
        num_client['Televisits'] = num_client['Televisits'].map('{:,.0f}'.format)
        num_client['Other'] = num_client['Other'].map('{:,.0f}'.format)
        num_client['Telemonitoring'] = num_client['Telemonitoring'].astype(str)                      
        numclient_tele = num_client[num_client['treat']==1]
        numclient_nontele = num_client[num_client['treat']==0]
        numclient_tele=numclient_tele.drop(['treat','Region'],axis=1)
        numclient_nontele=numclient_nontele.drop(['treat','Region','Year'],axis=1)
        numclient_nontele = numclient_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        numclient_tele.reset_index(drop=True,inplace=True)
        numclient_nontele.reset_index(drop=True, inplace=True)
        numclient_final = pd.concat([numclient_tele,numclient_nontele],axis=1)
        numclient_final = numclient_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        numclient_final = numclient_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        numclient_final = numclient_final.replace(to_replace = "0", value ="---")       


        postcost_inpat = inpat_df_postcost[inpat_df_postcost['Region']==sda_name]
        postcost_inpat = postcost_inpat.sort_values(by=['treat'])
        postcost_inpat=postcost_inpat.drop(['type','post','meas'],axis=1)
        postcost_inpat['Blind/Disabled'] = postcost_inpat['Blind/Disabled'].apply(np.round)
        postcost_inpat['Child'] = postcost_inpat['Child'].apply(np.round)
        postcost_inpat['Telemonitoring'] = postcost_inpat['Telemonitoring'].apply(np.round)
        postcost_inpat['Other'] = postcost_inpat['Other'].apply(np.round)
        postcost_inpat['Child'] = postcost_inpat['Child'].map('${:,.0f}'.format)
        postcost_inpat['Blind/Disabled'] = postcost_inpat['Blind/Disabled'].map('${:,.0f}'.format)
        postcost_inpat['Telemonitoring'] = postcost_inpat['Telemonitoring'].map('${:,.0f}'.format)
        postcost_inpat['Televisits'] = postcost_inpat['Televisits'].map('${:,.0f}'.format)
        postcost_inpat['Other'] = postcost_inpat['Other'].map('${:,.0f}'.format)
        postcost_tele_inpat = postcost_inpat[postcost_inpat['treat']==1]
        postcost_nontele_inpat = postcost_inpat[postcost_inpat['treat']==0]
        postcost_tele_inpat=postcost_tele_inpat.drop(['treat','Region'],axis=1)
        postcost_nontele_inpat=postcost_nontele_inpat.drop(['treat','Region','Year'],axis=1)
        postcost_nontele_inpat = postcost_nontele_inpat.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        postcost_tele_inpat.reset_index(drop=True,inplace=True)
        postcost_nontele_inpat.reset_index(drop=True, inplace=True)
        postcost_final_inpat = pd.concat([postcost_tele_inpat,postcost_nontele_inpat],axis=1)
        postcost_final_inpat = postcost_final_inpat[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        postcost_final_inpat = postcost_final_inpat.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        postcost_final_inpat = postcost_final_inpat.replace(to_replace = "$0", value ="---")   
        postcost_final_inpat = postcost_final_inpat.replace(to_replace = "$-0", value ="---")       

        inpat_encount_df = inpat_encount[inpat_encount['Region']==sda_name]
        inpat_encount_df = inpat_encount_df.sort_values(by=['treat'])
        inpat_encount_df=inpat_encount_df.drop(['type','post','meas'],axis=1)                      
        inpat_encount_df['Child'] = inpat_encount_df['Child'].map('{:,.3f}'.format)
        inpat_encount_df['Blind/Disabled'] = inpat_encount_df['Blind/Disabled'].map('{:,.3f}'.format)
        inpat_encount_df['Telemonitoring'] = inpat_encount_df['Telemonitoring'].map('{:,.3f}'.format)
        inpat_encount_df['Televisits'] = inpat_encount_df['Televisits'].map('{:,.3f}'.format)
        inpat_encount_df['Other'] = inpat_encount_df['Other'].map('{:,.3f}'.format)                
        inpat_encount_tele = inpat_encount_df[inpat_encount_df['treat']==1]
        inpat_encount_nontele = inpat_encount_df[inpat_encount_df['treat']==0]
        inpat_encount_tele=inpat_encount_tele.drop(['treat','Region'],axis=1)
        inpat_encount_nontele = inpat_encount_nontele.drop(['treat','Region','Year'],axis=1)
        inpat_encount_nontele = inpat_encount_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})     
        inpat_encount_tele.reset_index(drop=True,inplace=True)
        inpat_encount_nontele.reset_index(drop=True, inplace=True)   
        inpat_encount_final = pd.concat([inpat_encount_tele,inpat_encount_nontele],axis=1)      
        inpat_encount_final = inpat_encount_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        inpat_encount_final = inpat_encount_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})  
        inpat_encount_final = inpat_encount_final.replace(to_replace = "0.000", value ="---") 
        inpat_encount_final = inpat_encount_final.replace(to_replace = "-0.000", value ="---")   

        if sda_name != None:
            return render_template("inpatient.html", sda_name=sda_name, sda=sda, numclient_final=[numclient_final.to_html(index = False)],
                                    postcost_final_inpat=[postcost_final_inpat.to_html(index = False)],inpat_encount_final=[inpat_encount_final.to_html(index = False)])  
        
    return render_template('inpatient1.html',sda=sda, texas_numclient=[texas_numclient.to_html(index=False)], texas_postcost_inpat_final=[texas_postcost_inpat_final.to_html(index=False)], 
                            texas_inpat_encount_final=[texas_inpat_encount_final.to_html(index=False)])


@app.route('/edcost', methods=["GET", "POST"])
def edcost():
    if request.method == "POST":
        sda_name = request.form.get("sda", None)
        num_client = nclients[nclients['Region']==sda_name]
        num_client = num_client.sort_values(by=['treat'])
        num_client=num_client.drop(['type','post','meas'],axis=1)        
        num_client['Child'] = num_client['Child'].map('{:,.0f}'.format)
        num_client['Blind/Disabled'] = num_client['Blind/Disabled'].map('{:,.0f}'.format)        
        num_client['Telemonitoring'] = num_client['Telemonitoring'].map('{:,.0f}'.format)
        num_client['Televisits'] = num_client['Televisits'].map('{:,.0f}'.format)
        num_client['Other'] = num_client['Other'].map('{:,.0f}'.format)
        num_client['Telemonitoring'] = num_client['Telemonitoring'].astype(str)                      
        numclient_tele = num_client[num_client['treat']==1]
        numclient_nontele = num_client[num_client['treat']==0]
        numclient_tele=numclient_tele.drop(['treat','Region'],axis=1)
        numclient_nontele=numclient_nontele.drop(['treat','Region','Year'],axis=1)
        numclient_nontele = numclient_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        numclient_tele.reset_index(drop=True,inplace=True)
        numclient_nontele.reset_index(drop=True, inplace=True)
        numclient_final = pd.concat([numclient_tele,numclient_nontele],axis=1)
        numclient_final = numclient_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        numclient_final = numclient_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        numclient_final = numclient_final.replace(to_replace = "0", value ="---")      

        postcost_ed = ed_df_postcost[ed_df_postcost['Region']==sda_name]
        postcost_ed = postcost_ed.sort_values(by=['treat'])
        postcost_ed=postcost_ed.drop(['type','post','meas'],axis=1)
        postcost_ed['Blind/Disabled'] = postcost_ed['Blind/Disabled'].apply(np.round)
        postcost_ed['Child'] = postcost_ed['Child'].apply(np.round)
        postcost_ed['Telemonitoring'] = postcost_ed['Telemonitoring'].apply(np.round)
        postcost_ed['Other'] = postcost_ed['Other'].apply(np.round)
        postcost_ed['Child'] = postcost_ed['Child'].map('${:,.0f}'.format)
        postcost_ed['Blind/Disabled'] = postcost_ed['Blind/Disabled'].map('${:,.0f}'.format)
        postcost_ed['Telemonitoring'] = postcost_ed['Telemonitoring'].map('${:,.0f}'.format)
        postcost_ed['Televisits'] = postcost_ed['Televisits'].map('${:,.0f}'.format)
        postcost_ed['Other'] = postcost_ed['Other'].map('${:,.0f}'.format)
        postcost_tele_ed = postcost_ed[postcost_ed['treat']==1]
        postcost_nontele_ed = postcost_ed[postcost_ed['treat']==0]
        postcost_tele_ed=postcost_tele_ed.drop(['treat','Region'],axis=1)
        postcost_nontele_ed=postcost_nontele_ed.drop(['treat','Region','Year'],axis=1)
        postcost_nontele_ed = postcost_nontele_ed.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        postcost_tele_ed.reset_index(drop=True,inplace=True)
        postcost_nontele_ed.reset_index(drop=True, inplace=True)
        postcost_final_ed = pd.concat([postcost_tele_ed,postcost_nontele_ed],axis=1)
        postcost_final_ed = postcost_final_ed[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        postcost_final_ed = postcost_final_ed.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        postcost_final_ed = postcost_final_ed.replace(to_replace = "$0", value ="---")  
        postcost_final_ed = postcost_final_ed.replace(to_replace = "$-0", value ="---")      

        ed_visits_df = ed_visits[ed_visits['Region']==sda_name]
        ed_visits_df = ed_visits_df.sort_values(by=['treat'])
        ed_visits_df=ed_visits_df.drop(['type','post','meas'],axis=1)                      
        ed_visits_df['Child'] = ed_visits_df['Child'].map('{:,.3f}'.format)
        ed_visits_df['Blind/Disabled'] = ed_visits_df['Blind/Disabled'].map('{:,.3f}'.format)
        ed_visits_df['Telemonitoring'] = ed_visits_df['Telemonitoring'].map('{:,.3f}'.format)
        ed_visits_df['Televisits'] = ed_visits_df['Televisits'].map('{:,.3f}'.format)
        ed_visits_df['Other'] = ed_visits_df['Other'].map('{:,.3f}'.format)                
        ed_visits_tele = ed_visits_df[ed_visits_df['treat']==1]
        ed_visits_nontele = ed_visits_df[ed_visits_df['treat']==0]
        ed_visits_tele=ed_visits_tele.drop(['treat','Region'],axis=1)
        ed_visits_nontele=ed_visits_nontele.drop(['treat','Region','Year'],axis=1)
        ed_visits_nontele = ed_visits_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        ed_visits_tele.reset_index(drop=True,inplace=True)
        ed_visits_nontele.reset_index(drop=True, inplace=True)
        ed_visits_final = pd.concat([ed_visits_tele,ed_visits_nontele],axis=1)
        ed_visits_final = ed_visits_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        ed_visits_final = ed_visits_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        ed_visits_final = ed_visits_final.replace(to_replace = "0.000", value ="---")   
        ed_visits_final = ed_visits_final.replace(to_replace = "-0.000", value ="---")      

        if sda_name != None:
            return render_template("edcost.html", sda_name=sda_name, sda=sda, numclient_final=[numclient_final.to_html(index = False)],postcost_final_ed=[postcost_final_ed.to_html(index = False)],
                                    ed_visits_final=[ed_visits_final.to_html(index = False)])
    
    return render_template('edcost1.html',sda=sda, texas_numclient=[texas_numclient.to_html(index=False)], texas_postcost_ed_final=[texas_postcost_ed_final.to_html(index = False)]
                                        ,texas_ed_visits_final=[texas_ed_visits_final.to_html(index=False)])


@app.route('/outpatcost', methods=["GET", "POST"])
def outpatcost():
    if request.method == "POST":
        sda_name = request.form.get("sda", None)
        num_client = nclients[nclients['Region']==sda_name]
        num_client = num_client.sort_values(by=['treat'])
        num_client=num_client.drop(['type','post','meas'],axis=1)
        
        num_client['Child'] = num_client['Child'].map('{:,.0f}'.format)
        num_client['Blind/Disabled'] = num_client['Blind/Disabled'].map('{:,.0f}'.format)        
        num_client['Telemonitoring'] = num_client['Telemonitoring'].map('{:,.0f}'.format)
        num_client['Televisits'] = num_client['Televisits'].map('{:,.0f}'.format)
        num_client['Other'] = num_client['Other'].map('{:,.0f}'.format)
        num_client['Telemonitoring'] = num_client['Telemonitoring'].astype(str)
                      
        numclient_tele = num_client[num_client['treat']==1]
        numclient_nontele = num_client[num_client['treat']==0]
        numclient_tele=numclient_tele.drop(['treat','Region'],axis=1)
        numclient_nontele=numclient_nontele.drop(['treat','Region','Year'],axis=1)
        numclient_nontele = numclient_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        numclient_tele.reset_index(drop=True,inplace=True)
        numclient_nontele.reset_index(drop=True, inplace=True)
        numclient_final = pd.concat([numclient_tele,numclient_nontele],axis=1)

        numclient_final = numclient_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        numclient_final = numclient_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'}) 
        numclient_final = numclient_final.replace(to_replace = "0", value ="---")             

        postcost_outpat = outpat_df_postcost[outpat_df_postcost['Region']==sda_name]
        postcost_outpat = postcost_outpat.sort_values(by=['treat'])
        postcost_outpat=postcost_outpat.drop(['type','post','meas'],axis=1)
        postcost_outpat['Blind/Disabled'] = postcost_outpat['Blind/Disabled'].apply(np.round)
        postcost_outpat['Child'] = postcost_outpat['Child'].apply(np.round)
        postcost_outpat['Telemonitoring'] = postcost_outpat['Telemonitoring'].apply(np.round)
        postcost_outpat['Other'] = postcost_outpat['Other'].apply(np.round)
        postcost_outpat['Child'] = postcost_outpat['Child'].map('${:,.0f}'.format)
        postcost_outpat['Blind/Disabled'] = postcost_outpat['Blind/Disabled'].map('${:,.0f}'.format)
        postcost_outpat['Telemonitoring'] = postcost_outpat['Telemonitoring'].map('${:,.0f}'.format)
        postcost_outpat['Televisits'] = postcost_outpat['Televisits'].map('${:,.0f}'.format)
        postcost_outpat['Other'] = postcost_outpat['Other'].map('${:,.0f}'.format)
        postcost_tele_outpat = postcost_outpat[postcost_outpat['treat']==1]
        postcost_nontele_outpat = postcost_outpat[postcost_outpat['treat']==0]
        postcost_tele_outpat=postcost_tele_outpat.drop(['treat','Region'],axis=1)
        postcost_nontele_outpat=postcost_nontele_outpat.drop(['treat','Region','Year'],axis=1)
        postcost_nontele_outpat = postcost_nontele_outpat.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        postcost_tele_outpat.reset_index(drop=True,inplace=True)
        postcost_nontele_outpat.reset_index(drop=True, inplace=True)
        postcost_final_outpat = pd.concat([postcost_tele_outpat,postcost_nontele_outpat],axis=1)
        postcost_final_outpat = postcost_final_outpat[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        postcost_final_outpat = postcost_final_outpat.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        postcost_final_outpat = postcost_final_outpat.replace(to_replace = "$0", value ="---")  
        postcost_final_outpat = postcost_final_outpat.replace(to_replace = "$-0", value ="---")      

        outpat_visits_df = outpat_visits[outpat_visits['Region']==sda_name]
        outpat_visits_df = outpat_visits_df.sort_values(by=['treat'])
        outpat_visits_df=outpat_visits_df.drop(['type','post','meas'],axis=1)                      
        outpat_visits_df['Child'] = outpat_visits_df['Child'].map('{:,.3f}'.format)
        outpat_visits_df['Blind/Disabled'] = outpat_visits_df['Blind/Disabled'].map('{:,.3f}'.format)
        outpat_visits_df['Telemonitoring'] = outpat_visits_df['Telemonitoring'].map('{:,.3f}'.format)
        outpat_visits_df['Televisits'] = outpat_visits_df['Televisits'].map('{:,.3f}'.format)
        outpat_visits_df['Other'] = outpat_visits_df['Other'].map('{:,.3f}'.format)        
        outpat_visits_tele = outpat_visits_df[outpat_visits_df['treat']==1]
        outpat_visits_nontele = outpat_visits_df[outpat_visits_df['treat']==0]
        outpat_visits_tele = outpat_visits_tele.drop(['treat','Region'],axis=1)
        outpat_visits_nontele = outpat_visits_nontele.drop(['treat','Region','Year'],axis=1)
        outpat_visits_nontele = outpat_visits_nontele.rename(columns ={'Blind/Disabled':'Blind/Disabled_Comp','Child':'Child_Comp','Other':'Other_Comp',
                                                        'Televisits':'Televisits_Comp','Telemonitoring':'Telemonitoring_Comp'})
        outpat_visits_tele.reset_index(drop=True,inplace=True)
        outpat_visits_nontele.reset_index(drop=True, inplace=True)
        outpat_visits_final = pd.concat([outpat_visits_tele,outpat_visits_nontele],axis=1)
        outpat_visits_final = outpat_visits_final[["Year","Blind/Disabled","Blind/Disabled_Comp","Child","Child_Comp","Other","Other_Comp","Televisits","Televisits_Comp","Telemonitoring","Telemonitoring_Comp"]]
        outpat_visits_final = outpat_visits_final.rename(columns ={'Blind/Disabled':'Treatment','Blind/Disabled_Comp':'Comparison','Child':'Treatment','Child_Comp':'Comparison','Other':'Treatment',
                                                                'Other_Comp':'Comparison','Televisits':'Treatment','Televisits':'Treatment','Televisits_Comp':'Comparison','Telemonitoring':'Treatment',
                                                        'Telemonitoring_Comp':'Comparison'})
        outpat_visits_final = outpat_visits_final.replace(to_replace = "0.000", value ="---")      
        outpat_visits_final = outpat_visits_final.replace(to_replace = "-0.000", value ="---")      
    
        if sda_name != None:
            return render_template("outpatient.html", sda_name=sda_name, sda=sda, numclient_final=[numclient_final.to_html(index = False)],
            postcost_final_outpat=[postcost_final_outpat.to_html(index = False)], outpat_visits_final=[outpat_visits_final.to_html(index = False)])
    
    return render_template('outpatient1.html',sda=sda, texas_numclient=[texas_numclient.to_html(index=False)],   texas_postcost_outpat_final=[texas_postcost_outpat_final.to_html(index = False)],
                            texas_outpat_visits_final=[texas_outpat_visits_final.to_html(index=False)])




url1 = "./data/modifiedDemo.csv"
sda_demo = []

df_demo = pd.read_csv(url1,error_bad_lines=False)
df_demo = df_demo.rename(columns={'rgrp31':'Child-Treat', 'rgrp32':'Child-Comp',  'rgrp41': 'Blind/Disabled-Treat', 'rgrp42':'Blind/Disabled-Comp',
                                'rgrp61':'Telemonitoring-Treat','rgrp62':'Telemonitoring-Comp','sfy':'Year','SDA' : 'Region','demo':'Demographic'})
df_demo = df_demo[['Region','Year','Demographic','Child-Treat','Child-Comp','Blind/Disabled-Treat','Blind/Disabled-Comp','Telemonitoring-Treat','Telemonitoring-Comp','ord']]
df_demo = df_demo.fillna(0)
df_demo = df_demo.drop(['ord'],axis=1)
sda_demo = (df_demo['Region'].unique())
sda_demo = np.roll(sda_demo,2)
sda_demo = sda_demo[sda_demo!=0]
df_demo.loc[df_demo.Demographic == "N","Demographic"] = "Number of Clients"
texas_demo = df_demo[df_demo['Region']=='Texas']

values = []
format_values = []
values=[texas_demo['Child-Treat'].iloc[0],texas_demo['Child-Treat'].iloc[8],texas_demo['Child-Treat'].iloc[16],texas_demo['Child-Treat'].iloc[24],texas_demo['Child-Treat'].iloc[32],
        texas_demo['Child-Treat'].iloc[40],texas_demo['Child-Comp'].iloc[0],texas_demo['Child-Comp'].iloc[8],texas_demo['Child-Comp'].iloc[16],texas_demo['Child-Comp'].iloc[24],texas_demo['Child-Comp'].iloc[32],
        texas_demo['Child-Comp'].iloc[40],texas_demo['Blind/Disabled-Treat'].iloc[0],texas_demo['Blind/Disabled-Treat'].iloc[8],texas_demo['Blind/Disabled-Treat'].iloc[16],texas_demo['Blind/Disabled-Treat'].iloc[24],texas_demo['Blind/Disabled-Treat'].iloc[32],
        texas_demo['Blind/Disabled-Treat'].iloc[40],texas_demo['Blind/Disabled-Comp'].iloc[0],texas_demo['Blind/Disabled-Comp'].iloc[8],texas_demo['Blind/Disabled-Comp'].iloc[16],texas_demo['Blind/Disabled-Comp'].iloc[24],texas_demo['Blind/Disabled-Comp'].iloc[32],
        texas_demo['Blind/Disabled-Comp'].iloc[40],texas_demo['Telemonitoring-Treat'].iloc[0],texas_demo['Telemonitoring-Treat'].iloc[8],texas_demo['Telemonitoring-Treat'].iloc[16],texas_demo['Telemonitoring-Treat'].iloc[24],texas_demo['Telemonitoring-Treat'].iloc[32],
        texas_demo['Telemonitoring-Treat'].iloc[40],texas_demo['Telemonitoring-Comp'].iloc[0],texas_demo['Telemonitoring-Comp'].iloc[8],texas_demo['Telemonitoring-Comp'].iloc[16],texas_demo['Telemonitoring-Comp'].iloc[24],texas_demo['Telemonitoring-Comp'].iloc[32],
        texas_demo['Telemonitoring-Comp'].iloc[40]]
for i in values: 
    i = round(i,2)
    i = "{:,.0f}".format(i)
    format_values.append(i)
texas_demo['Child-Treat'] = texas_demo['Child-Treat'].map('{:,.2f}'.format)
x = 0
j = 0
for i in range(6):
    texas_demo['Child-Treat'].iloc[x] = format_values[j]
    x+=8
    j+=1
texas_demo['Child-Comp'] = texas_demo['Child-Comp'].map('{:,.2f}'.format)
x = 0
j = 6
for i in range(6):
    texas_demo['Child-Comp'].iloc[x] = format_values[j]
    x+=8
    j+=1
texas_demo['Blind/Disabled-Treat'] = texas_demo['Blind/Disabled-Treat'].map('{:,.2f}'.format)
x = 0
j = 12
for i in range(6):
    texas_demo['Blind/Disabled-Treat'].iloc[x] = format_values[j]
    x+=8
    j+=1
texas_demo['Blind/Disabled-Comp'] = texas_demo['Blind/Disabled-Comp'].map('{:,.2f}'.format)
x = 0
j = 18
for i in range(6):
    texas_demo['Blind/Disabled-Comp'].iloc[x] = format_values[j]
    x+=8
    j+=1
texas_demo['Telemonitoring-Treat'] = texas_demo['Telemonitoring-Treat'].map('{:,.2f}'.format)
x = 0
j = 24
for i in range(6):
    texas_demo['Telemonitoring-Treat'].iloc[x] = format_values[j]
    x+=8
    j+=1
texas_demo['Telemonitoring-Comp'] = texas_demo['Telemonitoring-Comp'].map('{:,.2f}'.format)
x = 0
j = 30
for i in range(6):
    texas_demo['Telemonitoring-Comp'].iloc[x] = format_values[j]
    x+=8
    j+=1
texas_demo = texas_demo.rename(columns={'Child-Treat':'Treatment', 'Child-Comp':'Comparison',  'Blind/Disabled-Treat':'Treatment','Blind/Disabled-Comp':'Comparison',
                                'Telemonitoring-Treat':'Treatment','Telemonitoring-Comp': 'Comparison','Demographic':'Characteristics'})
texas_demo = texas_demo.replace(to_replace = "0.00", value ="---")
texas_demo = texas_demo.drop(['Region'],axis=1)

texas_2013 = texas_demo[texas_demo['Year']==2013]
texas_2014 = texas_demo[texas_demo['Year']==2014]
texas_2015 = texas_demo[texas_demo['Year']==2015]
texas_2016 = texas_demo[texas_demo['Year']==2016]
texas_2017 = texas_demo[texas_demo['Year']==2017]
texas_2018 = texas_demo[texas_demo['Year']==2018]


values1 = []
format_values1 = []
@app.route('/demographics', methods = ["GET","POST"])
def demographics(): 
    if request.method == "POST":
        sda_demo_name = request.form.get('sda_demo',None)
        region_demo = df_demo[df_demo['Region']==sda_demo_name]
        values1=[region_demo['Child-Treat'].iloc[0],region_demo['Child-Treat'].iloc[8],region_demo['Child-Treat'].iloc[16],region_demo['Child-Treat'].iloc[24],region_demo['Child-Treat'].iloc[32],
        region_demo['Child-Treat'].iloc[40],region_demo['Child-Comp'].iloc[0],region_demo['Child-Comp'].iloc[8],region_demo['Child-Comp'].iloc[16],region_demo['Child-Comp'].iloc[24],region_demo['Child-Comp'].iloc[32],
        region_demo['Child-Comp'].iloc[40],region_demo['Blind/Disabled-Treat'].iloc[0],region_demo['Blind/Disabled-Treat'].iloc[8],region_demo['Blind/Disabled-Treat'].iloc[16],region_demo['Blind/Disabled-Treat'].iloc[24],region_demo['Blind/Disabled-Treat'].iloc[32],
        region_demo['Blind/Disabled-Treat'].iloc[40],region_demo['Blind/Disabled-Comp'].iloc[0],region_demo['Blind/Disabled-Comp'].iloc[8],region_demo['Blind/Disabled-Comp'].iloc[16],region_demo['Blind/Disabled-Comp'].iloc[24],region_demo['Blind/Disabled-Comp'].iloc[32],
        region_demo['Blind/Disabled-Comp'].iloc[40],region_demo['Telemonitoring-Treat'].iloc[0],region_demo['Telemonitoring-Treat'].iloc[8],region_demo['Telemonitoring-Treat'].iloc[16],region_demo['Telemonitoring-Treat'].iloc[24],region_demo['Telemonitoring-Treat'].iloc[32],
        region_demo['Telemonitoring-Treat'].iloc[40],region_demo['Telemonitoring-Comp'].iloc[0],region_demo['Telemonitoring-Comp'].iloc[8],region_demo['Telemonitoring-Comp'].iloc[16],region_demo['Telemonitoring-Comp'].iloc[24],region_demo['Telemonitoring-Comp'].iloc[32],
        region_demo['Telemonitoring-Comp'].iloc[40]]
        for i in values1: 
            i = round(i,2)
            i = "{:,.0f}".format(i)
            format_values.append(i)
        region_demo['Child-Treat'] = region_demo['Child-Treat'].map('{:,.2f}'.format)
        x = 0
        j = 0
        for i in range(6):
            region_demo['Child-Treat'].iloc[x] = format_values[j]
            x+=8
            j+=1
        region_demo['Child-Comp'] = region_demo['Child-Comp'].map('{:,.2f}'.format)
        x = 0
        j = 6
        for i in range(6):
            region_demo['Child-Comp'].iloc[x] = format_values[j]
            x+=8
            j+=1
        region_demo['Blind/Disabled-Treat'] = region_demo['Blind/Disabled-Treat'].map('{:,.2f}'.format)
        x = 0
        j = 12
        for i in range(6):
            region_demo['Blind/Disabled-Treat'].iloc[x] = format_values[j]
            x+=8
            j+=1
        region_demo['Blind/Disabled-Comp'] = region_demo['Blind/Disabled-Comp'].map('{:,.2f}'.format)
        x = 0
        j = 18
        for i in range(6):
            region_demo['Blind/Disabled-Comp'].iloc[x] = format_values[j]
            x+=8
            j+=1       
        region_demo['Telemonitoring-Treat'] = region_demo['Telemonitoring-Treat'].map('{:,.2f}'.format)
        x = 0
        j = 24
        for i in range(6):
            region_demo['Telemonitoring-Treat'].iloc[x] = format_values[j]
            x+=8
            j+=1
        region_demo['Telemonitoring-Comp'] = region_demo['Telemonitoring-Comp'].map('{:,.2f}'.format)
        x = 0
        j = 30
        for i in range(6):
            region_demo['Telemonitoring-Comp'].iloc[x] = format_values[j]
            x+=8
            j+=1
        region_demo = region_demo.rename(columns={'Child-Treat':'Treatment', 'Child-Comp':'Comparison',  'Blind/Disabled-Treat':'Treatment','Blind/Disabled-Comp':'Comparison',
                                'Telemonitoring-Treat':'Treatment','Telemonitoring-Comp': 'Comparison','Demographic':'Characteristics'})
        region_demo = region_demo.replace(to_replace = "0.00", value ="---")
        region_demo = region_demo.drop(['Region'],axis=1)                                
        region_2013 = region_demo[region_demo['Year']==2013]
        region_2014 = region_demo[region_demo['Year']==2014]
        region_2015 = region_demo[region_demo['Year']==2015]
        region_2016 = region_demo[region_demo['Year']==2016]
        region_2017 = region_demo[region_demo['Year']==2017]
        region_2018 = region_demo[region_demo['Year']==2018]
        if sda_demo_name != None:
            return render_template('demographics.html',sda_demo=sda_demo, sda_demo_name=sda_demo_name, region_2013=[region_2013.to_html(index=False,classes='demo')], region_2014=[region_2014.to_html(index=False,classes='demo')],
                                    region_2015=[region_2015.to_html(index=False,classes='demo')], region_2016=[region_2016.to_html(index=False,classes='demo')],  region_2017=[region_2017.to_html(index=False,classes='demo')],
                                    region_2018=[region_2018.to_html(index=False,classes='demo')])
    return render_template('demographics1.html',sda_demo=sda_demo, texas_2013=[texas_2013.to_html(index=False,classes='demo')], texas_2014=[texas_2014.to_html(index=False,classes='demo')],
                            texas_2015=[texas_2015.to_html(index=False,classes='demo')],texas_2016=[texas_2016.to_html(index=False,classes='demo')],texas_2017=[texas_2017.to_html(index=False,classes='demo')],
                            texas_2018=[texas_2018.to_html(index=False,classes='demo')])


url2 = "./data/sda_smmry.csv"
sda_hosp = []
df_hosp = pd.read_csv(url2,error_bad_lines=False)
df_hosp = df_hosp.rename(columns={'ccsr':'Condition','year':'Year','n_hospitalizations': 'Hospitalization Count','avg_los':'Avg Length of Stay',
                            'std_los':'Std Dev Length of Stay','avg_chrg':'Avg Charges','std_chrg':'Std Dev Charges'})
df_hosp = df_hosp.drop(['lci_chrg','uci_chrg','lci_los','uci_los','Obs'],axis=1)


df_hosp=df_hosp.replace(to_replace=".", value =0)
df_hosp['Std Dev Length of Stay'] = df_hosp['Std Dev Length of Stay'].astype(float)
df_hosp['Std Dev Charges'] = df_hosp['Std Dev Charges'].astype(float)
df_hosp['Hospitalization Count'] = df_hosp['Hospitalization Count'].map('{:,.0f}'.format)
df_hosp['Avg Charges'] = df_hosp['Avg Charges'].map('${:,.0f}'.format)
df_hosp['Avg Length of Stay'] = df_hosp['Avg Length of Stay'].map('{:,.2f}'.format)
df_hosp['Std Dev Length of Stay'] = df_hosp['Std Dev Length of Stay'].map('{:,.2f}'.format)
df_hosp['Std Dev Charges'] = df_hosp['Std Dev Charges'].map('${:,.0f}'.format)



sda_hosp = df_hosp['SDA'].unique()
sda_hosp = np.roll(sda_hosp,2)

texas_hosp = df_hosp[df_hosp['SDA']=='Texas']
texas_hosp = texas_hosp.drop(['SDA'],axis=1)
texas_mental = texas_hosp.loc[texas_hosp['Condition'].isin(['Alcohol-related disorders','Depressive disorders',
                                        'Schizophrenia spectrum and other psychotic disorders'])]

@app.route('/mental-health', methods = ["GET","POST"])
def mental_health():
    if request.method == "POST":
        sda_hosp_name = request.form.get('sda_hosp',None)
        region_hosp = df_hosp[df_hosp['SDA']==sda_hosp_name]
        region_hosp = region_hosp.drop(['SDA'],axis=1)
        region_mental = region_hosp.loc[region_hosp['Condition'].isin(['Alcohol-related disorders','Depressive disorders',
                                        'Schizophrenia spectrum and other psychotic disorders'])]

        if sda_hosp_name != None:
            return render_template('mental_health.html',sda_hosp=sda_hosp,sda_hosp_name=sda_hosp_name, region_mental = [region_mental.to_html(index=False)])

    return render_template('mental_health1.html',sda_hosp=sda_hosp, texas_mental=[texas_mental.to_html(index=False)])


texas_heart =  texas_hosp.loc[texas_hosp['Condition'].isin(['Acute myocardial infarction','Cardiac and circulatory congenital anomalies',
                                        'Heart failure','Hypertension and hypertensive-related conditions complicating pregnancy; childbirth; and the puerperium','MACE Event'])]

@app.route('/heart-conditions',methods = ["GET","POST"])
def heart_conditions():
    if request.method == "POST":
        sda_hosp_name = request.form.get('sda_hosp',None)
        region_hosp = df_hosp[df_hosp['SDA']==sda_hosp_name]
        region_hosp = region_hosp.drop(['SDA'],axis=1)
        region_heart = region_hosp.loc[region_hosp['Condition'].isin(['Acute myocardial infarction','Cardiac and circulatory congenital anomalies',
                                        'Heart failure','Hypertension and hypertensive-related conditions complicating pregnancy; childbirth; and the puerperium','MACE Event'])]
        
        
        if sda_hosp_name != None:
            return render_template('heart_condition.html',sda_hosp=sda_hosp,sda_hosp_name=sda_hosp_name, region_heart = [region_heart.to_html(index=False)])


    return render_template('heart_condition1.html',sda_hosp=sda_hosp, texas_heart=[texas_heart.to_html(index=False)])

''' start marg additions
'''
@app.route('/demo-6-month-follow-up', methods=("POST", "GET"))
def demo_6mo():
    fn = './data/tmon_cntrl_demo.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
                'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat = demo_subset(fn, sda, 1)
    df_comp = demo_subset(fn, sda, 0)
    return render_template('demo.html', 
        title_header=sda,
        table_treat=[df_treat.to_html(classes='data', index=False)],
        table_comp=[df_comp.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-telemonitoring-6-month-follow-up', methods=("POST", "GET"))
def cost_tm_6mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_tm = cost_subset(fn, sda, 1, 1)
    return render_template('cost_tm.html', 
        title_header=sda,
        tbl_tmon=[df_treat_tm.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-mace-serious-6-month-follow-up', methods=("POST", "GET"))
def cost_mser_6mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mser = cost_subset(fn, sda, 1, 3)
    df_comp_mser = cost_subset(fn, sda, 0, 3)
    return render_template('cost_mser.html', 
        title_header=sda,
        tbl_trt_ser=[df_treat_mser.to_html(classes='data', index=False)],
        tbl_cmp_ser=[df_comp_mser.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-mace-non-serious-6-month-follow-up', methods=("POST", "GET"))
def cost_mot_6mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mot = cost_subset(fn, sda, 1, 4)
    df_comp_mot = cost_subset(fn, sda, 0, 4)
    return render_template('cost_mot.html', 
        title_header=sda,
        tbl_trt_ot=[df_treat_mot.to_html(classes='data', index=False)],
        tbl_cmp_ot=[df_comp_mot.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-mace-total-6-month-follow-up', methods=("POST", "GET"))
def cost_mtot_6mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mtot = cost_subset(fn, sda, 1, 2)
    df_comp_mtot = cost_subset(fn, sda, 0, 2)
    return render_template('cost_mtot.html', 
        title_header=sda,
        tbl_trt_tot=[df_treat_mtot.to_html(classes='data', index=False)],
        tbl_cmp_tot=[df_comp_mtot.to_html(classes='data', index=False)],
        menu_items=menu_items)

''' 12 mo follow up
'''
@app.route('/demo-12-month-follow-up', methods=("POST", "GET"))
def demo_12mo():
    fn = './data/tmon_cntrl_demo.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
                'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat = demo_subset(fn, sda, 1)
    df_comp = demo_subset(fn, sda, 0)
    return render_template('demo.html', 
        title_header=sda,
        table_treat=[df_treat.to_html(classes='data', index=False)],
        table_comp=[df_comp.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-telemonitoring-12-month-follow-up', methods=("POST", "GET"))
def cost_tm_12mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_tm = cost_subset(fn, sda, 1, 1)
    return render_template('cost_tm.html', 
        title_header=sda,
        tbl_tmon=[df_treat_tm.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-mace-serious-12-month-follow-up', methods=("POST", "GET"))
def cost_mser_12mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mser = cost_subset(fn, sda, 1, 3)
    df_comp_mser = cost_subset(fn, sda, 0, 3)
    return render_template('cost_mser.html', 
        title_header=sda,
        tbl_trt_ser=[df_treat_mser.to_html(classes='data', index=False)],
        tbl_cmp_ser=[df_comp_mser.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-mace-non-serious-12-month-follow-up', methods=("POST", "GET"))
def cost_mot_12mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mot = cost_subset(fn, sda, 1, 4)
    df_comp_mot = cost_subset(fn, sda, 0, 4)
    return render_template('cost_mot.html', 
        title_header=sda,
        tbl_trt_ot=[df_treat_mot.to_html(classes='data', index=False)],
        tbl_cmp_ot=[df_comp_mot.to_html(classes='data', index=False)],
        menu_items=menu_items)

@app.route('/cost-mace-total-12-month-follow-up', methods=("POST", "GET"))
def cost_mtot_12mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mtot = cost_subset(fn, sda, 1, 2)
    df_comp_mtot = cost_subset(fn, sda, 0, 2)
    return render_template('cost_mtot.html', 
        title_header=sda,
        tbl_trt_tot=[df_treat_mtot.to_html(classes='data', index=False)],
        tbl_cmp_tot=[df_comp_mtot.to_html(classes='data', index=False)],
        menu_items=menu_items)

'''hptn
'''
@app.route('/demo-hptn-6-month-follow-up', methods=("POST", "GET"))
def demo_hptn_6mo():
    fn = './data/tmon_cntrl_demo_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
                'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat = demo_subset(fn, sda, 1)
    df_comp = demo_subset(fn, sda, 0)
    return render_template('demo.html', 
        title_header=sda,
        table_treat=[df_treat.to_html(classes='data', index=False)],
        table_comp=[df_comp.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-telemonitoring-hptn-6-month-follow-up', methods=("POST", "GET"))
def cost_tm_hptn_6mo():
    fn = './data/tmon_cntrl_costs_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_tm = cost_subset(fn, sda, 1, 1)
    return render_template('cost_tm.html', 
        title_header=sda,
        tbl_tmon=[df_treat_tm.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-mace-serious-hptn-6-month-follow-up', methods=("POST", "GET"))
def cost_mser_hptn_6mo():
    fn = './data/tmon_cntrl_costs_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mser = cost_subset(fn, sda, 1, 3)
    df_comp_mser = cost_subset(fn, sda, 0, 3)
    return render_template('cost_mser.html', 
        title_header=sda,
        tbl_trt_ser=[df_treat_mser.to_html(classes='data', index=False)],
        tbl_cmp_ser=[df_comp_mser.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-mace-non-serious-hptn-6-month-follow-up', methods=("POST", "GET"))
def cost_mot_hptn_6mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mot = cost_subset(fn, sda, 1, 4)
    df_comp_mot = cost_subset(fn, sda, 0, 4)
    return render_template('cost_mot.html', 
        title_header=sda,
        tbl_trt_ot=[df_treat_mot.to_html(classes='data', index=False)],
        tbl_cmp_ot=[df_comp_mot.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-mace-total-hptn-6-month-follow-up', methods=("POST", "GET"))
def cost_mtot_hptn_6mo():
    fn = './data/tmon_cntrl_costs_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mtot = cost_subset(fn, sda, 1, 2)
    df_comp_mtot = cost_subset(fn, sda, 0, 2)
    return render_template('cost_mtot.html', 
        title_header=sda,
        tbl_trt_tot=[df_treat_mtot.to_html(classes='data', index=False)],
        tbl_cmp_tot=[df_comp_mtot.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)


'''12 mo follow up
'''
@app.route('/demo-hptn-12-month-follow-up', methods=("POST", "GET"))
def demo_hptn_12mo():
    fn = './data/tmon_cntrl_demo_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
                'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat = demo_subset(fn, sda, 1)
    df_comp = demo_subset(fn, sda, 0)
    return render_template('demo.html', 
        title_header=sda,
        table_treat=[df_treat.to_html(classes='data', index=False)],
        table_comp=[df_comp.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-telemonitoring-hptn-12-month-follow-up', methods=("POST", "GET"))
def cost_tm_hptn_12mo():
    fn = './data/tmon_cntrl_costs_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_tm = cost_subset(fn, sda, 1, 1)
    return render_template('cost_tm.html', 
        title_header=sda,
        tbl_tmon=[df_treat_tm.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-mace-serious-hptn-12-month-follow-up', methods=("POST", "GET"))
def cost_mser_hptn_12mo():
    fn = './data/tmon_cntrl_costs_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mser = cost_subset(fn, sda, 1, 3)
    df_comp_mser = cost_subset(fn, sda, 0, 3)
    return render_template('cost_mser.html', 
        title_header=sda,
        tbl_trt_ser=[df_treat_mser.to_html(classes='data', index=False)],
        tbl_cmp_ser=[df_comp_mser.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-mace-non-serious-hptn-12-month-follow-up', methods=("POST", "GET"))
def cost_mot_hptn_12mo():
    fn = './data/tmon_cntrl_costs.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mot = cost_subset(fn, sda, 1, 4)
    df_comp_mot = cost_subset(fn, sda, 0, 4)
    return render_template('cost_mot.html', 
        title_header=sda,
        tbl_trt_ot=[df_treat_mot.to_html(classes='data', index=False)],
        tbl_cmp_ot=[df_comp_mot.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)

@app.route('/cost-mace-total-hptn-12-month-follow-up', methods=("POST", "GET"))
def cost_mtot_hptn_12mo():
    fn = './data/tmon_cntrl_costs_hptn.csv'
    menu_items = ['Texas', 'MRSA West', 'MRSA Northeast', 'MRSA Central', 'Dallas SDA', 'Nueces SDA', 
    'Lubbock SDA', 'Jefferson SDA', 'Tarrant SDA', 'Hidalgo SDA']
    if request.method == 'POST':
        sda = request.form.get('menu_items')
        menu_items = [sda] + [item for item in menu_items if item != sda]
    else:
        sda = 'Texas'
    df_treat_mtot = cost_subset(fn, sda, 1, 2)
    df_comp_mtot = cost_subset(fn, sda, 0, 2)
    return render_template('cost_mtot.html', 
        title_header=sda,
        tbl_trt_tot=[df_treat_mtot.to_html(classes='data', index=False)],
        tbl_cmp_tot=[df_comp_mtot.to_html(classes='data', index=False)],
        menu_items=menu_items,
        hptn=True)



''' end marg additions
'''
if __name__ == "__main__":
    app.run(debug=True) 
