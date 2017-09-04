## Installing `plotly, pandas, sqlalchemy, scipy, numpy` and `matplotlib` with bundled `Python (3.6)` using `pynsist`. 

##### Short Overview:

Packaging these libraries can be tricky because they each require an number of `.dll` files to work. Rather than manually specifying each DLL required, here's a simple way to package these libraries without too much hassle. 

1. `matplotlib` - build it from wheels, under the `pypi-wheels` section of `installer.cfg`. Also, as mentioned in other examples, `matplotlib` additionally requires the `six, pyparsing` and `dateutil` libraries to be manually specified in `installer.cfg`

2. `numpy/scipy` - Packaging these on Windows is a little involved due to `numpy's` reliance on Intel's proprietary `MKL` libraries, and `scipy's` reliance on a few DLLs. The solution is as follows:
    1) Go to http://www.lfd.uci.edu/~gohlke/pythonlibs/, and download the pre-compiled numpy/scipy binaries. You will notice that the `numpy` binaries are specified as `numpy + mkl`, which is a good thing. 
    2) Navigate to the directory in which the `.whl` files were downloaded. Change the `.whl` extension to `.zip`.
    3) Extract both zipped files directly into the same directory containing `installer.cfg`
    4) In `installer.cfg`, include the following lines. A full example can be found in the `installer.cfg` file associated with this writeup. 
        - `numpy` > `$INSTDIR\pkgs`
        - `numpy-1.13.1+mkl.data > $InSTDIR\pkgs`
        - `numpy-1.13.1+mkl.dist-info > $INSTDIR\pkgs`
	    - `scipy > $INSTDIR\pkgs`
	    - `scipy-0.19.1.dist-info > $INSTDIR\pkgs`

3. `plotly`: can be specified under the `package` section, and requires `pprint`, `pkg_resources`, `requests` and `decorator` as additional dependencies.

4. `pandas`: can be specified under the `package` section, and requires `pytz, six, setuptools` and `dateutils` as additional dependencies.

5. `sqlalchemy`: can be specified under the `package` section, and requires `psycopg2` as an additional dependency if one is connecting to a PostgreSQL server. `psycopg2` should be specified under the `pypi-wheels` section to avoid `DLL`-based `ImportErrors`.
