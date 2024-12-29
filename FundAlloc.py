import pandas as pd

import numpy as np
from PIL import Image
import pulp
import time
import streamlit as st
img  = Image.open("Logo.png")
st.set_page_config(
    page_title="FundAlloc",
    page_icon=img
)
st.markdown("<h1 style='color: #4287f5 ; text-align:center;'>AI-Driven Mutal Fund App</h1>" , unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center ; color:#EF9917;'>Now decide your own <span style='color:red;'>risk</span> and <span style='color:green;'>return</span>! </h2>" , unsafe_allow_html=True)
data= pd.read_excel("stock_data3.xlsx")
data.set_index("Fund" , inplace=True)
funds = data.index
num={}

for i in range(funds.size):

    num[funds[i]]=i

weights = []

for i in range (10):

    weights.append(0.01 + i*0.02)

def find(x):

    prob = pulp.LpProblem("max_returns" , pulp.LpMaximize)

    select = pulp.LpVariable.dicts("selection" ,funds, 0 , 1 , pulp.LpBinary)

    allocation = pulp.LpVariable.dicts("allocate" ,funds, 0 , 1 , pulp.LpContinuous)

    prob+= pulp.lpSum(select[fund] for fund in funds)==5

    prob+= pulp.lpSum(allocation[fund] for fund in funds)==1

    for fund in funds:

        prob+= allocation[fund]>= 0.1*select[fund]

        prob+= allocation[fund]<= 0.35*select[fund]

    for i in range (10):

        prob+= sum(allocation[fund]*data.iloc[num[fund] , i] for fund in funds) >= x

    prob+= sum(sum(allocation[fund]*data.iloc[num[fund] , i] for fund in funds)*weights[i] for i in range(10))

    prob.solve()
    with st.spinner(":timer_clock: Optimzing your portfolio.. "):
           time.sleep(2)
    if(prob.status == pulp.LpStatusInfeasible):
        st.warning("Your enetered value is too high to gaurantee!!:expressionless:")
        return
    selected_funds = [fund for fund in funds if pulp.value(select[fund])>0.5]

    allocation_funds = {fund: pulp.value(allocation[fund]) for fund in selected_funds}
    st.markdown("### :orange[Your portfolio allocation :pizza: :]")
    final = pd.DataFrame({"Fund":selected_funds , "allocation(in %)":[round((pulp.value(allocation[fund]))*100, 2) for fund in selected_funds]}, index=[i+1  for i in range(5)])

    st.dataframe(final)

    s=0

    for i in range(10):

        s=s+ sum(pulp.value(allocation[fund])*data.iloc[num[fund] , i] for fund in funds)*weights[i]
    ret=[]
    k= round(s,2)

    for i in range(10):

        ret.append(round(sum(pulp.value(allocation[fund])*data.iloc[num[fund] , i] for fund in funds),2))
    st.markdown("## :green[Last 10 years performance] :chart_with_upwards_trend: :")
    st.dataframe(pd.DataFrame({"year":[str(2014+i) for i in range(10)] , "return(in %)":ret} , index=[i+1 for i in range(10)]))
    st.markdown(f"## :orange[Average annual return is:] :green[{str(round(s,2))+"%"}] :smile:")
y = st.number_input(label="Enter the min(%) annual return you can tolerate in a bad market year (E.g: Enter -7.00 for -7% , 5.00 for +5%):")
if st.button("Get me the best portfolio"):
    find(y)
