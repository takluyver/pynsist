import streamlit as st
import plotly.graph_objects as go

st.title("My first Streamlit app deployed with pynsist!")

st.write("Example plotly graphs follows")

fig = go.Figure(go.Scatter(x=[1, 2], y=[1, 2], name="trace", mode="lines"))
st.plotly_chart(fig, use_container_width=True)

