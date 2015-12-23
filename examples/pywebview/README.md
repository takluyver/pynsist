This is an example [Pywebview](https://github.com/r0x0r/pywebview) application
built using Pynsist.

First, run `./download.sh` to fetch and unpack the necessary Windows libraries.
Then build with:

    pynsist installer.cfg

At present, the user must separately install the MS Visual C++ 2010 redistributable,
because pywin32 is compiled using that.

http://www.microsoft.com/en-us/download/details.aspx?id=14632
