"""
This example demonstrates how to create a webview window.

Adapted from a pywebview example:
https://github.com/r0x0r/pywebview/blob/master/examples/simple_browser.py
"""

import webview

def main():
    # Create a non-resizable webview window with 800x600 dimensions
    webview.create_window("Simple browser", "http://pynsist.readthedocs.io/",
                            width=800, height=600, resizable=False)

if __name__ == '__main__':
    main()
