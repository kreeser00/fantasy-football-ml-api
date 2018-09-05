from app.exception.SerializedObjectException import SerializedObjectException
from app.exception.ExceptionCodes import ExceptionCodes
from app.util.SerializedFileFormats import SerializedFileFormats
import logging
from app.logger.CustomLogger import CustomLogger
from app.constants.ModelConstants import ModelConstants

import app.config.ModelConfig as model_config

model_name = model_config.model_name

if model_name == ModelConstants.MODEL_NAME_BTU:
    from keras.models import load_model
else:
    from sklearn.externals import joblib    

logger = CustomLogger(logging.INFO).get_custom_logger()


class SerializedObjectHelper:

    def load_serialized_object(self, model_path, device_version_serialized_object_dict):

        device_version_serialized_object_data_dict= {}
      
        for device_version, serialized_object_name in device_version_serialized_object_dict.items():
            serialized_object_name = serialized_object_name.strip()
            file_extension = serialized_object_name.split(".")[1]
            try:
                if file_extension == SerializedFileFormats.PICKLE.value:
                    data = (joblib.load(model_path + '/' + serialized_object_name))
                elif file_extension == SerializedFileFormats.HDF5.value:
                    data = load_model(model_path + '/' + serialized_object_name)
            except Exception as ex:
                error_message = ExceptionCodes.ERROR_LOADING_PICKLE.value %(serialized_object_name)
                logger.error(str(ex), extra={'packagename': None, 'modelname':None})
                raise SerializedObjectException(error_message)

            device_version_serialized_object_data_dict[device_version] = data

        return device_version_serialized_object_data_dict
