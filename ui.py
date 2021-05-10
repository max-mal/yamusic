#!/usr/bin/env python3

from app.ui.main import Ui
import logging
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		
def main(args):    

	ui = Ui()
	ui.init()        	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
