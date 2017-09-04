import matplotlib.pyplot as plt 
import pandas as pd 
from sqlalchemy import create_engine
import plotly.plotly as py  
import plotly.graph_objs as go 
import numpy as np 
from scipy.interpolate import interp1d

# set up plotly credentials for publishing purposes. 
import plotly
plotly.tools.set_credentials_file(username='test_user', api_key='123456')


# Note: This file does not actually execute. It is just an example file to show
# what an application containing these components could look like. 

def main():
    # connect to a database using SQLAlchemy.
    username, password = 'testuser', 'testpassword'
    engine = create_engine('postgresql://' + username + ':' + password + 'database_url')
    connection = engine.connect() 
    query = "user-defined-query"

    # pandas
    df = pd.read_sql(query, connection)
    x1 = df.col1.values 
    x2 = df.col2.values 

    # numpy 
    x1[np.isnan(x1)] = 0 
    x2[np.isnan(x2)] = 0 

    # scipy 
    f1 = interp1d(x1, x2, fill_value='extrapolate')

    # matplotlib
    plt.scatter(x1.values, x2.values, 'mpl_scatter')
    plt.plot(x1.values, f1(x1.values), 'scipy interpolation')
    plt.show()

    # create a few sample graph objects. 
    trace = go.Scatter(
        x=x1,
        y=x2,
        name='test_plot')

    data = [trace]
    py.plot(data, filename='plotly_basic_scatter')
