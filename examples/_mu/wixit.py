import os
from subprocess import run, CalledProcessError
import sys

WIX_BIN = os.path.join(os.environ['WIX'], 'bin')

def wix(cmd, *args):
	cmd = os.path.join(WIX_BIN, cmd)
	run([cmd] + list(args), check=True)
	
try:
	print('Running candle (wxs to wixobj)')
	wix('candle', 'files.wxs')
	wix('candle', 'wrapper.wxs')
	print('Running light (wixobj to msi)')
	wix('light', 'files.wixobj', 'wrapper.wixobj', '-o', 'mu_editor.msi', '-b', 'build\\nsis')
except CalledProcessError:
	sys.exit(1)