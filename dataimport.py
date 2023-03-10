import nimbalwear
import os
import pandas as pd
from utilities import convert_time_columns


def import_imu_data(file_dict: dict,
                    full_id: str, visit_num: str,
                    leftwrist: bool = False,
                    rightwrist: bool = False,
                    leftankle: bool = False,
                    rightankle: bool = False,
                    bittium: bool = False):
    dict_out = {}

    filenames = {'lw': file_dict['axivity_file'].format(full_id, visit_num, 'L', 'Wrist'),
                 'rw': file_dict['axivity_file'].format(full_id, visit_num, 'R', 'Wrist'),
                 'la': file_dict['axivity_file'].format(full_id, visit_num, 'L', 'Ankle'),
                 'ra': file_dict['axivity_file'].format(full_id, visit_num, 'R', 'Ankle'),
                 'bf': file_dict['bittium_file'].format(full_id, visit_num)}

    available_files = {'lw': leftwrist and os.path.exists(filenames['lw']),
                       'rw': rightwrist and os.path.exists(filenames['rw']),
                       'la': leftankle and os.path.exists(filenames['la']),
                       'ra': rightankle and os.path.exists(filenames['rw']),
                       'bf': bittium and os.path.exists(filenames['bf'])}

    for key in available_files:
        if available_files[key]:
            dict_out[key] = nimbalwear.Device()
            dict_out[key].import_edf(filenames[key])

            if 'start_datetime' in dict_out[key].header.keys():
                start_key = 'start_datetime'
            if 'start_time' in dict_out[key].header.keys():
                start_key = 'start_time'
            if 'startdate' in dict_out[key].header.keys():
                start_key = 'startdate'

            channel_labels = [i['label'] for i in dict_out[key].signal_headers]

            dict_out[key].ts = pd.date_range(start=dict_out[key].header[start_key],
                                             periods=len(dict_out[key].signals[0]),
                                             freq="{}ms".format(1000 / dict_out[key].signal_headers[0]["sample_rate"]))

            if 'Temperature' in channel_labels:
                temp_idx = dict_out[key].get_signal_index('Temperature')
                temp_fs = dict_out[key].signal_headers[temp_idx]["sample_rate"]

                dict_out[key].temp_ts = pd.date_range(start=dict_out[key].header[start_key],
                                                      periods=len(dict_out[key].signals[temp_idx]),
                                                      freq="{}ms".format(1000 / temp_fs))
            if 'Temperature' not in channel_labels:
                dict_out[key].signal_headers.append({'label': 'taco',
                                                     'transducer': 'nothing',
                                                     'dimension': 'C',
                                                     'sample_dr': 5,
                                                     'sample_rate': 1.25,
                                                     'physical_max': 100,
                                                     'physical_min': -273,
                                                     'digital_max': 32676,
                                                     'digital_min': -32768,
                                                     'prefilter': ""})
                dict_out[key].signals.append([])
                dict_out[key].temp_ts = []

    return dict_out


def import_tabular(file_dict):

    dict_out = {}

    # Gait bouts ---------------------------------------------------------------------------------
    if os.path.exists(file_dict['gait_bouts']):

        dict_out['gait_bouts'] = pd.read_csv(file_dict['gait_bouts'])
        dict_out['gait_bouts'] = convert_time_columns(dict_out['gait_bouts'])

        dict_out['gait_bouts'].rename(columns={"start_timestamp": "start_time",
                                               "end_timestamp": "end_time"}, inplace=True)

        dict_out['gait_bouts']['duration'] = [(row.end_time - row.start_time).total_seconds() for
                                              row in dict_out['gait_bouts'].itertuples()]
        dict_out['gait_bouts']['cadence'] = dict_out['gait_bouts']['step_count'] / \
                                            dict_out['gait_bouts']['duration'] * 60

    if not os.path.exists(file_dict['gait_bouts']):
        dict_out['gait_bouts'] = pd.DataFrame(columns=['study_code', 'subject_id', 'coll_id', 'gait_bout_num',
                                                       'start_time', 'end_time', 'step_count', 'duration', 'cadence'])

    # Steps --------------------------------------------------------------------------------------
    if os.path.exists(file_dict['steps']):
        dict_out['steps'] = pd.read_csv(file_dict['steps'])
        dict_out['steps'] = convert_time_columns(dict_out['steps'])
        dict_out['steps'].rename(columns={"step_time": "start_time"}, inplace=True)

    if not os.path.exists(file_dict['steps']):
        dict_out['steps'] = pd.DataFrame(columns=['study_code', 'subject_id', 'coll_id', 'step_num',
                                                  'gait_bout_num', 'step_idx', 'start_time'])

    # Sleep --------------------------------------------------------------------------------------
    if os.path.exists(file_dict['sleep']):
        dict_out['sleep'] = pd.read_csv(file_dict['sleep'])

        dict_out['sleep'].rename(columns={"start_timestamp": "start_time",
                                          "end_timestamp": "end_time"}, inplace=True)

        dict_out['sleep'] = convert_time_columns(dict_out['sleep'])
        dict_out['sleep']['duration'] = [(row.end_time - row.start_time).total_seconds() / 3600 for
                                         row in dict_out['sleep'].itertuples()]

    if not os.path.exists(file_dict['sleep']):
        dict_out['sleep'] = pd.DataFrame(columns=['study_code', 'subject_id', 'coll_id', 'sptw_num', 'relative_date',
                                                  'start_time', 'end_time', 'overnight', 'duration'])

    # Nonwear ------------------------------------------------------------------------------------

    nw_cols = ['study_code', 'subject_id', 'coll_id', 'device_type',
               'device_location', 'event', 'start_time', 'end_time']

    for body_loc in ['rw', 'lw', 'ra', 'la']:
        if os.path.exists(file_dict[f'{body_loc}_nw']):
            dict_out[f'{body_loc}_nw'] = pd.read_csv(file_dict[f'{body_loc}_nw'])

            dict_out[f'{body_loc}_nw'].rename(columns={"start_timestamp": "start_time",
                                              "end_timestamp": "end_time"}, inplace=True)

            dict_out[f'{body_loc}_nw'] = dict_out[f'{body_loc}_nw'].loc[dict_out[f'{body_loc}_nw']['event'] == 'nonwear']

            dict_out[f'{body_loc}_nw'] = convert_time_columns(dict_out[f'{body_loc}_nw'])
            dict_out[f'{body_loc}_nw']['duration'] = [(row.end_time - row.start_time).total_seconds() for
                                                      row in dict_out[f'{body_loc}_nw'].itertuples()]

            dict_out[f'{body_loc}_nw'] = dict_out[f'{body_loc}_nw'][nw_cols]

        if not os.path.exists(file_dict[f'{body_loc}_nw']):
            dict_out[f"{body_loc}_nw"] = pd.DataFrame(columns=nw_cols)

    return dict_out


def import_epoch(file_dict):

    dict_out = {}

    # Right wrist AVM ---------------------------------------------------------------------------
    if os.path.exists(file_dict['rw_epoch']):
        dict_out['rw_epoch'] = pd.read_csv(file_dict['rw_epoch'])

        dict_out['rw_epoch'].rename(columns={"start_timestamp": "start_time",
                                             "end_timestamp": "end_time"}, inplace=True)

        dict_out['rw_epoch'] = convert_time_columns(dict_out['rw_epoch'])

    if not os.path.exists(file_dict['rw_epoch']):
        dict_out['rw_epoch'] = pd.DataFrame(columns=['study_code', 'subject_id', 'coll_id', 'activity_epoch_num',
                                                     'device_location', 'cutpoint_type', 'cutpoint_dominant',
                                                     'start_time', 'end_time', 'avm', 'intensity'])

    # Left wrist AVM ----------------------------------------------------------------------------

    if os.path.exists(file_dict['lw_epoch']):
        dict_out['lw_epoch'] = pd.read_csv(file_dict['lw_epoch'])

        dict_out['lw_epoch'].rename(columns={"start_timestamp": "start_time",
                                             "end_timestamp": "end_time"}, inplace=True)

        dict_out['lw_epoch'] = convert_time_columns(dict_out['lw_epoch'])

    if not os.path.exists(file_dict['lw_epoch']):
        dict_out['lw_epoch'] = pd.DataFrame(columns=['study_code', 'subject_id', 'coll_id', 'activity_epoch_num',
                                                     'device_location', 'cutpoint_type', 'cutpoint_dominant',
                                                     'start_time', 'end_time', 'avm', 'intensity'])

    return dict_out
