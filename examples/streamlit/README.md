# Streamlit deployment via `pynsist`

This is an example on how to deploy a streamlit app using `pynsist`. The example also includes the required packages to run plotly inside the app.

The extra wheels of the package `blinker`is required (can't be found on Pypi).

[Here](https://stackoverflow.com/questions/69352179/package-streamlit-app-and-run-executable-on-windows/69621578#69621578) you can find additional information on why the `src/run_app.py` has the chosen structure.

The browser tab with the app should open automatically after a brief delay. This is done to avoid the tab opening while streamlit is still starting, so that this results in a `Cannot reach localhost:8501` error.


