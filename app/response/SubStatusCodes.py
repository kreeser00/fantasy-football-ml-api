from enum import Enum


class ResponseSubStatusCodes(Enum):
    FF_4001 = "Invalid GlobalParameters"
    FF_4002 = "Invalid InputParameters"
    PY_4003 = "Input request has insufficient data"
    FF_4004 = "Invalid PredictionLevel"
    FF_4005 = "PredictionLevel Mismatch"
    FF_5001 = "Error in Model Validation"
    FF_5002 = "Error in Model Transformation"
    FF_5003 = "Error in Model Prediction"
    FF_5004 = "Invalid Model"
    FF_5005 = "General Error"
    FF_5006 = "Invalid Model Mapping"
    FF_5007 = "Invalid Model Prediction Response JSON Structure"
