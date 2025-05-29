
from ._text_normalizer import TextNormalizer
from configs import configs
from logger import logger

def make_text_normalizer():
    """
    Create a text normalizer instance.

    This function initializes and returns a text normalizer that can be used
    to process and normalize text data.
    """
    resources = {
        "logger": logger,
    }
    return TextNormalizer(resources=resources, configs=configs)  # Assuming TextNormalizer is the class to be instantiated.
