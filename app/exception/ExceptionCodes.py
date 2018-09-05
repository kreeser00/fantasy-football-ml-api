from enum import Enum


class ExceptionCodes(Enum):
    ERROR_LOADING_PICKLE = "Error loading pickle %s. Please check if pickle exists or pickle load path is correct"
    PREDICTION_LEVEL_ALL_INVALID_MODEL_PREDICTION_DATA = "Only single prediction value per prediction label is " + \
                                                         "valid when predictionLevel is ALL"
    PREDICTION_LEVEL_ROW_INVALID_MODEL_PREDICTION_DATA = "Number of predictions for a given label should be equal " + \
                                                         "to the number of arrays in Values array in request when " + \
                                                         "predictionLevel is ROW"
