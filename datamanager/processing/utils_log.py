import logging


dm_logger = logging.getLogger("datamanager")
dm_logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)
dm_logger.addHandler(stream_handler)


def add_file_logger(file_path: str):
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    dm_logger.addHandler(file_handler)
    
    
# def log_info(msg: str):
#     if dm_logger is not None:
#         dm_logger.info(msg)
#     else:
#         pass
        
        
# def log_warning(msg: str):
#     dm_logger.warning(msg)
        
        
# def log_error(msg: str):
#     dm_logger.error(msg)