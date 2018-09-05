from flask import Flask, request, jsonify
from pandas.core.frame import DataFrame
from jsonschema import validate

import json, pandas as pd, ast, logging, datetime, numpy as np
import jsonschema

from app.exception.PredictionLevelException import PredictionLevelException
from app.exception.RequestDataException import RequestDataException
from app.exception.ExceptionCodes import ExceptionCodes

from app.constants.RequestConstants import RequestConstants
from app.constants.ResponseConstants import ResponseConstants
from app.constants.ModelConstants import ModelConstants

from app.util.SerializedObjectHelper import SerializedObjectHelper

from app.request.PredictionLevels import PredictionLevels

from app.response.StatusCodes import ResponseStatusCodes
from app.response.SubStatusCodes import ResponseSubStatusCodes

from app.util.FantasyFootballOffense import calc_past_offensive_fantasy_value

from app.logger.CustomLogger import CustomLogger

import app.config.ModelConfig as model_config
import app.data as model_data
import app.validation_schema as validation_schema

app = Flask(__name__)

app.config.from_object('app.config.Config')

validation_schema_dir = validation_schema.__path__[0]

serialized_object_helper = SerializedObjectHelper()
requestConstants = RequestConstants()
responseConstants = ResponseConstants()
modelConstants = ModelConstants()

model_name = model_config.model_name
offerings_name=model_config.offerings_name
serialized_model_mapping_json = model_config.device_serialized_object_mapping

if bool(serialized_model_mapping_json):
    device_version_serialized_object_dict = ast.literal_eval(serialized_model_mapping_json)
else:
    device_version_serialized_object_dict = {}

if bool(device_version_serialized_object_dict):
    serialized_object_path = model_data.__path__[0]
    device_version_serializedObjectData_dict = \
        serialized_object_helper.load_serialized_object(serialized_object_path, device_version_serialized_object_dict)
else:
    device_version_serializedObjectData_dict = {}

logger = CustomLogger(logging.INFO).get_custom_logger()

device_version_input_type_dict = {}
device_version_num_of_values_rows_dict = {}
device_version_prediction_level_dict = {}


@app.route('/health', methods=['GET'])
def health():
    try:
        logger.info("Received request for health..........", extra={'modelname': None})
        return jsonify({"result":"Working Fine... model_name: " + model_name + " offerings_name: " + offerings_name })

    except Exception as ex:
            return "exception thrown by health endpoint is: " + str(ex)


@app.route("/" + offerings_name + "/" + model_name + '/predict', methods=['POST'])
def predict_model():

    request_json = request.get_json()

    logger.info("Received Request for POST predict.... Request Json is" + str(request_json),
                extra={'modelname': model_name})

    try:
        device_version_data_frame_dict = __get_device_version_data_frame_dictionary(request_json)
    except KeyError as ex:
        error_json = __get_error_dict(ResponseStatusCodes.ERROR.value,
                                      ResponseStatusCodes.ERROR.name,
                                      ResponseSubStatusCodes.FF_4002.name,
                                      ResponseSubStatusCodes.FF_4002.value +
                                      ": " + str(ex) + responseConstants.RESPONSE_MESSAGE_REQUEST_ELEMENT_MISSING)
        logger.error("POST predict. Invalid request InputParameters......." + str(ex),
                     extra={'modelname': model_name})
        return json.dumps(error_json, sort_keys=True)
    except RequestDataException as ex:
        allowed_prediction_levels= ','.join(map(str,[e.value for e in PredictionLevels]) )
        error_json = __get_error_dict(ResponseStatusCodes.ERROR.value,
                                      ResponseStatusCodes.ERROR.name,
                                      ResponseSubStatusCodes.FF_4004.name,
                                      ResponseSubStatusCodes.FF_4004.value +
                                      responseConstants.RESPONSE_MESSAGE_ALLOWED_VALUES + allowed_prediction_levels)
        logger.error("POST predict........" + str(ex) + responseConstants.RESPONSE_MESSAGE_ALLOWED_VALUES +
                     allowed_prediction_levels,
                     extra={'modelname': model_name})
        return json.dumps(error_json, sort_keys=True)
    except Exception as ex:
        error_json = __get_error_dict(ResponseStatusCodes.INTERNAL_SERVER_ERROR.value,
                                      ResponseStatusCodes.INTERNAL_SERVER_ERROR.name,
                                      ResponseSubStatusCodes.FF_5005.name,
                                      ResponseSubStatusCodes.FF_5005.value)
        logger.error("POST predict. An error occurred during the creation of data frames......." + str(ex),
                         extra={'modelname': model_name})
        return json.dumps(error_json, sort_keys=True)

    if not device_version_data_frame_dict:
        error_json = __get_error_dict(ResponseStatusCodes.ERROR.value,
                                      ResponseStatusCodes.ERROR.name,
                                      ResponseSubStatusCodes.FF_4003.name,
                                      ResponseSubStatusCodes.FF_4003.value)
        logger.error("POST predict. No data available to create data frames..........."+str(error_json),
                         extra={'modelname':model_name})
        return json.dumps(error_json, sort_keys=True)
    else:
        for key, val in device_version_data_frame_dict.items():
            if DataFrame(val).empty:
                error_json = __get_error_dict(ResponseStatusCodes.ERROR.value,
                                              ResponseStatusCodes.ERROR.name,
                                              ResponseSubStatusCodes.FF_4003.name,
                                              ResponseSubStatusCodes.FF_4003.value)
                logger.error("POST predict. No data available to create data frames for device name: " + key +
                             "............." + str(error_json),
                             extra={'modelname':model_name})
                return json.dumps(error_json, sort_keys=True)

    try:
        is_validated = True
        if device_version_data_frame_dict['year'].dtype != np.int64:
            is_validated = False
    except Exception as ex:
        error_json = __get_error_dict(ResponseStatusCodes.INTERNAL_SERVER_ERROR.value,
                                      ResponseStatusCodes.INTERNAL_SERVER_ERROR.name,
                                      ResponseSubStatusCodes.FF_5001.name,
                                      ResponseSubStatusCodes.FF_5001.value)
        logger.error("POST predict. Model validation routine raised an error......." + str(ex),
                     extra={'modelname': model_name})
        return json.dumps(error_json, sort_keys=True)

    if is_validated:
        try:
            predicted_value_json = __predict(device_version_serializedObjectData_dict, device_version_data_frame_dict)
        except Exception as ex:
            error_json = __get_error_dict(ResponseStatusCodes.INTERNAL_SERVER_ERROR.value,
                                          ResponseStatusCodes.INTERNAL_SERVER_ERROR.name,
                                          ResponseSubStatusCodes.FF_5003.name,
                                          ResponseSubStatusCodes.FF_5003.value)
            logger.error("POST predict. Model Prediction routine raised an error......." + str(ex),
                         extra={'modelname': model_name})
            return json.dumps(error_json, sort_keys=True)

        if not __is_valid_predict_response(predicted_value_json):
            error_json = __get_error_dict(ResponseStatusCodes.INTERNAL_SERVER_ERROR.value,
                                          ResponseStatusCodes.INTERNAL_SERVER_ERROR.name,
                                          ResponseSubStatusCodes.FF_5007.name, ResponseSubStatusCodes.FF_5007.value)
            logger.error("POST predict. Model Prediction returned json in an invalid structure.......",
                         extra={'modelname': model_name})
            return json.dumps(error_json, sort_keys=True)

        try:
            response_json = __create_success_response(request_json, predicted_value_json)
        except PredictionLevelException as ex:
            error_json = __get_error_dict(ResponseStatusCodes.ERROR.value,
                                          ResponseStatusCodes.ERROR.name,
                                          ResponseSubStatusCodes.FF_4005.name,
                                          ResponseSubStatusCodes.FF_4005.value +
                                          ". " + str(ex))
            error_message = "POST predict. Model Prediction returned json with invalid data " + \
                            "violating predictionlevel policy......."
            logger.error(error_message + str(ex), extra={'modelname': model_name})
            return json.dumps(error_json, sort_keys=True)

        logger.info("POST predict. Prediction Response Json is ...... " + str(response_json),
                    extra={'modelname': model_name})

        return json.dumps(response_json, sort_keys=True)

    else:
        error_json = __get_error_dict(ResponseStatusCodes.INTERNAL_SERVER_ERROR.value,
                                      ResponseStatusCodes.INTERNAL_SERVER_ERROR.name,
                                      ResponseSubStatusCodes.FF_5004.name,
                                      ResponseSubStatusCodes.FF_5004.value)
        logger.error("POST predict. Model Validation failed. Invalid Model......" + str(error_json),
                     extra={'modelname': model_name})
        return json.dumps(error_json, sort_keys=True)


"""
Method to return a dictionary with the following Key-Value pairs
Key: device_version (comes from the requestBody in the request json for the API)
Value: DataFrame (created from columnNames as data frame header and values as data frame rows. columnNames and values
                  are the elements in the request json for the API)
"""


def __get_device_version_data_frame_dictionary(request_json):

    device_inputs = request_json[requestConstants.REQUEST_ELEMENT_INPUTPARAMETERS]

    device_version_data_frame_dict = {}

    for value in device_inputs.values():
        device_version = value[requestConstants.REQUEST_ELEMENT_NAME]
        column_names = value[requestConstants.REQUEST_ELEMENT_COLUMNNAMES]
        row_data  = value[requestConstants.REQUEST_ELEMENT_VALUES]
        input_type = value[requestConstants.REQUEST_ELEMENT_TYPE]
        prediction_level = value[requestConstants.REQUEST_ELEMENT_PREDICTIONLEVEL]

        if prediction_level not in [e.value for e in PredictionLevels]:
            raise RequestDataException(ResponseSubStatusCodes.FF_4004.value)

        df = pd.DataFrame(row_data, columns=column_names)

        device_version_data_frame_dict[device_version] = df
        device_version_input_type_dict[device_version] = input_type
        device_version_num_of_values_rows_dict[device_version] = len(row_data)
        device_version_prediction_level_dict[device_version] = prediction_level

    return device_version_data_frame_dict


def __create_success_response(request_json, predicted_value_json):
    response_json = {}

    response_json[responseConstants.RESPONSE_ELEMENT_RESULTS] = {}

    ResponseParameters = {}
    ResponseParameters[responseConstants.RESPONSE_ELEMENT_REQUEST_DATE] = str(datetime.datetime.now())
    ResponseParameters[responseConstants.RESPONSE_ELEMENT_RESPONSE_CODE] = ResponseStatusCodes.OK.value
    ResponseParameters[responseConstants.RESPONSE_ELEMENT_RESPONSE_MESSAGE] = ResponseStatusCodes.OK.name

    response_json[responseConstants.RESPONSE_ELEMENT_RESULTS][responseConstants.RESPONSE_ELEMENT_RESPONSEPARAMETERS] = ResponseParameters

    response_json[responseConstants.RESPONSE_ELEMENT_RESULTS][requestConstants.REQUEST_ELEMENT_INPUTPARAMETERS] = request_json[requestConstants.REQUEST_ELEMENT_INPUTPARAMETERS]

    OutputParameters = {}

    # Note: Right now we assume that there would be just one Input in the request.
    #      So there would be just one item in v.values()
    #      In future when we deal with multiple inputs, this code can be leveraged for that
    #      where OutputParameters would be an array of Output elements
    for v in predicted_value_json.values():
        # The following for loop can be used once system supports multiple inputs
        val = list(v.values())[0]
        Output = {}
        device_version = val[modelConstants.DEVICE_VERSION]
        Output[responseConstants.RESPONSE_ELEMENT_TYPE] = device_version_input_type_dict[device_version]
        Output[responseConstants.RESPONSE_ELEMENT_NAME] = device_version
        prediction_level = device_version_prediction_level_dict[device_version]
        Output[responseConstants.RESPOSNE_ELEMENT_PREDICTIONLEVEL] = prediction_level
        Output[responseConstants.RESPONSE_ELEMENT_COLUMNS] = list(val[modelConstants.PREDICTIONS].keys())
        Values = []

        for pred_value in val[modelConstants.PREDICTIONS].values():
            if not __does_prediction_data_match_prediction_level (device_version, pred_value):
                if prediction_level == PredictionLevels.ALL.value:
                    raise PredictionLevelException(ExceptionCodes.PREDICTION_LEVEL_ALL_INVALID_MODEL_PREDICTION_DATA.value)
                else:
                    raise PredictionLevelException(ExceptionCodes.PREDICTION_LEVEL_ROW_INVALID_MODEL_PREDICTION_DATA.value)
            Values.append(pred_value)

        # we need have the same number of rows for Values element in output as in the Input.
        Values_numpy = np.array(Values)
        Values_numpy_Transpose = Values_numpy.T
        Values_numpy_Transpose_list = Values_numpy_Transpose.tolist()

        Output[responseConstants.RESPONSE_ELEMENT_VALUES] = Values_numpy_Transpose_list
        OutputParameters[responseConstants.RESPONSE_ELEMENT_OUTPUT] = Output

    response_json[responseConstants.RESPONSE_ELEMENT_RESULTS][responseConstants.RESPONSE_ELEMENT_OUTPUTPARAMETERS] = OutputParameters

    return response_json


'''
This method determines if the response of Predict life cycle routine is as per the PredictionLevel
request element.
'''


def __does_prediction_data_match_prediction_level(device_version, device_version_pred_value):

    if (device_version_prediction_level_dict[device_version] == PredictionLevels.ALL.value
        and len(device_version_pred_value) != 1) \
        or \
       (device_version_prediction_level_dict[device_version] == PredictionLevels.ROW.value
        and len(device_version_pred_value) != device_version_num_of_values_rows_dict[device_version]):
            return False

    return True


def __get_error_dict(status_code, status_message, sub_status, sub_status_message):

    error_sub_status = {responseConstants.RESPONSE_ELEMENT_RESPONSE_SUBSTATUS_CODE: sub_status,
                        responseConstants.RESPONSE_ELEMENT_RESPONSE_SUBSTATUS_MESSAGE: sub_status_message}

    response_params = {responseConstants.RESPONSE_ELEMENT_REQUEST_DATE: str(datetime.datetime.now()),
                       responseConstants.RESPONSE_ELEMENT_RESPONSE_CODE : status_code,
                       responseConstants.RESPONSE_ELEMENT_RESPONSE_MESSAGE : status_message,
                       responseConstants.RESPONSE_ELEMENT_RESPONSE_ERROR_SUBSTATUS: error_sub_status}

    results = {responseConstants.RESPONSE_ELEMENT_RESPONSEPARAMETERS: response_params}

    error_json = {responseConstants.RESPONSE_ELEMENT_RESULTS: results}

    return error_json


def __is_valid_predict_response(predicted_value_json):
    predict_response_schema_file_path = validation_schema_dir + "/predict_response_json_schema.json"
    with open(predict_response_schema_file_path, 'r') as my_file:
        predict_response_schema_string = my_file.read().replace('\n', '')

    predict_response_schema_json = json.loads(predict_response_schema_string)

    try:
        validate(predicted_value_json, predict_response_schema_json)
    except (jsonschema.exceptions.ValidationError, jsonschema.SchemaError):
        return False

    return True


def __predict(device_version_pickle_data_dict, transformed_device_version_object_dict):
    device_version_dict_count = 0
    intermediate_results = {}
    final_prediction_dict = {}

    games_df = None
    first_year_dict = dict()
    for player_id in games_df.player_id.unique():
        game_list = games_df.loc[games_df.player_id == player_id]
        if game_list is not None and len(game_list) > 0:
            for index, row in game_list.iterrows():
                if 8 <= row.date.month <= 12:
                    season_year = row.date.year
                else:
                    season_year = row.date.year - 1

                if first_year_dict.get(player_id) is None:
                    first_year_dict[player_id] = int(season_year)
                else:
                    if int(season_year) < first_year_dict.get(player_id):
                        first_year_dict[player_id] = int(season_year)

    for key, value in sorted(transformed_device_version_object_dict.iteritems()):

        device_version_dict_count += 1

        results_key = "Results"
        predictions_dict = {}
        predicted_fantasy_values_dict = {}
        year = value[0]

        games_last_season = games_df.loc[games_df['season'] == year - 1]

        # loop through the games for last season
        for player_id in games_last_season.player_id.unique():
            game_list = games_last_season.loc[games_last_season.player_id == player_id]
            if game_list is not None and len(game_list) > 0:
                value_last_season = calc_past_offensive_fantasy_value(game_list, year - 1)
                first_year = first_year_dict.get(player_id)
                years_played = 0
                if first_year is not None:
                    years_played = year - first_year + 1
                pa_array = np.array([years_played])
                pa_value = device_version_pickle_data_dict.predict(pa_array[:, np.newaxis])
                value_next_season = value_last_season + (1.5 * pa_value[0])
                predicted_fantasy_values_dict[player_id] = [value_next_season]
        # predictions = .predict(year).tolist()

        predictions_dict['device_version'] = str(key)
        predictions_dict['Predictions'] = predicted_fantasy_values_dict

        intermediate_results[results_key] = predictions_dict

    final_prediction_dict["PredictionResults"] = intermediate_results

    return final_prediction_dict

    # 6. Make QB predictions for next year
    # nextYearDict = dict()
    # get all games from the year previous
    # gamesForLastSeason = gamesDf.loc[gamesDf['season'] == 2017]
    # loop through the games for last season
    # for player_id in gamesForLastSeason.player_id.unique():
    #    gameList = gamesForLastSeason.loc[gamesForLastSeason.player_id == player_id]
    #    if gameList is not None and len(gameList) > 0:
    #        lastSeasonValue = calcPastOffensiveFantasyValue(gameList,2017)
    #        firstYear = firstYearDict.get(player_id)
    #        years_played = 0
    #        if firstYear is not None:
    #            years_played = nextSeason - firstYear + 1
    #        print("Player ID: ", player_id)
    #        nextSeasonValuePredict = predictOffensiveFantasyValue(pa_model,lastSeasonValue,years_played)
    #        pred2018Dict[player_id] = [nextSeasonValuePredict]
    # pred2018Df = pd.DataFrame.from_dict(pred2018Dict).transpose()
    # pred2018Df.columns = ['fantasyvalue']
    # pred2018Df.sort_values(by=['fantasyvalue'],ascending=False,inplace=True)
    # return device_version_predictionList_dict


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # uncomment this line for local testing and comment the previous one
    # app.run(host='127.0.0.1',port=app.config['SERVER_PORT'])
