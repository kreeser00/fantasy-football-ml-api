import os
import json
import logging
import logging.config
import app.config as log_config


class CustomLogger():
    
    default_flask_logger = 'werkzeug'
    
    def __init__(self, no_log_file_default_log_level):
        path = log_config.__path__[0] + "/logging_properties.json"
        try:
            self.__disable_default_flask_logger()
            
            if os.path.exists(path):        
                with open(path, 'rt') as f:
                    config = json.load(f)
                logging.config.dictConfig(config)  
                self._my_logger = logging.getLogger("customLogger")
            else:           
                self._my_logger = self.__get_custom_default_logger(no_log_file_default_log_level)
                
        except Exception as ex:
            logging.error("An error occurred while creating a log entry............. " + str(ex))

    def __disable_default_flask_logger(self):
        try: 
            log = logging.getLogger(self.default_flask_logger)
            log.setLevel(logging.INFO)
            log.propagate=False
        except Exception as ex:
            logging.error("An error occurred while disabling python default logger at " + str(ex))

    def __get_custom_default_logger(self, no_log_file_default_log_level):
        logger = logging.getLogger('rootLogger')
        logger.setLevel(logging.INFO)
         
        handler = logging.StreamHandler()
        handler.setLevel(no_log_file_default_log_level)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(modelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def get_custom_logger(self):
        try:
            return self._my_logger
        except Exception as ex:
            logging.error("Custom _my_logger is not initialized due to an exception....... " + str(ex))
            return None
