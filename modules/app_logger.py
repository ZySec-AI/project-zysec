
import logging


def setup_logger():
    # Format for our loglines
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # Setup basic configuration for logging
    logging.basicConfig(filename='app.log', 
                        level=logging.ERROR, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Create a logger
    logger = logging.getLogger('AppLogger')

    # Create handlers (if you want to log to file and console)
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

app_logger = setup_logger()