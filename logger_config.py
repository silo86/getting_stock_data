import logging, io
from datetime import datetime

class LoggerConfig:
    def __init__(self):
        logging.basicConfig(filename='fetch_log.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
        self.stringIO = io.StringIO()
        self.streamhandler = logging.StreamHandler(self.stringIO)
        self.logger = None
    
    def get_logger(self, name = None):
        self.logger = logging.getLogger(name)
        self.logger.addHandler(self.streamhandler)
        return self.logger

    def get_filename(self):
        datetimeStr = datetime.now().strftime("%Y%m%d%H%M%S")
        return f'log{datetimeStr}.log'