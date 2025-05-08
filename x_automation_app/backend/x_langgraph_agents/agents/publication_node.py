import time
from ..tools.utils import WorkflowState
import logging

def publication_node(state: WorkflowState):
    logging.info("\n\n---------- Publishing the tweet... ----------\n\n")
    time.sleep(10)
    logging.info("---------- Tweet published!!! ----------")