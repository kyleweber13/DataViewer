from dataimport import import_imu_data, import_tabular, import_epoch
from plotting import plot_data

full_id = 'OND09_SBH0402'
visit_num = '01'

file_dict = {'axivity_file': "W:/NiMBaLWEAR/OND09/wearables/device_edf_cropped/{}_{}_AXV6_{}{}.edf",
             'bittium_file': "W:/NiMBaLWEAR/OND09/wearables/device_edf_cropped/{}_{}_BF36_Chest.edf",
             'gait_bouts': f"W:/NiMBaLWEAR/OND09/analytics/gait/bouts/{full_id}_{visit_num}_GAIT_BOUTS.csv",
             'steps': f"W:/NiMBaLWEAR/OND09/analytics/gait/steps/{full_id}_{visit_num}_GAIT_STEPS.csv",
             # 'activity_log': "W:/OND09 (HANDDS-ONT)/Digitized logs/handds_activity_log.xlsx",
             'sleep':  f"W:/NiMBaLWEAR/OND09/analytics/sleep/sptw/{full_id}_{visit_num}_SPTW.csv",
             'rw_epoch': f"W:/NiMBaLWEAR/OND09/analytics/activity/epochs/{full_id}_{visit_num}_ACTIVITY_EPOCHS.csv",
             'lw_epoch': "",
             'wrist_avm_1s': f"W:/NiMBaLWEAR/OND09/analytics/activity/epochs/{full_id}_{visit_num}_ACTIVITY_EPOCHS.csv",
             'rw_nw': f"W:/NiMBaLWEAR/OND09/analytics/nonwear/bouts_cropped/{full_id}_{visit_num}_AXV6_RWrist_NONWEAR.csv",
             'lw_nw': f"W:/NiMBaLWEAR/OND09/analytics/nonwear/bouts_cropped/{full_id}_{visit_num}_AXV6_LWrist_NONWEAR.csv",
             'ra_nw': f"W:/NiMBaLWEAR/OND09/analytics/nonwear/bouts_cropped/{full_id}_{visit_num}_AXV6_RAnkle_NONWEAR.csv",
             "la_nw": f"W:/NiMBaLWEAR/OND09/analytics/nonwear/bouts_cropped/{full_id}_{visit_num}_AXV6_LAnkle_NONWEAR.csv",
             "bf_nw": ""}

imu_data = import_imu_data(file_dict=file_dict, full_id=full_id, visit_num=visit_num,
                           leftwrist=False, rightwrist=True, leftankle=False, rightankle=True)

tab_data = import_tabular(file_dict)

epoch_data = import_epoch(file_dict)

imu_plot_dict = {"rw": {"axis": ['Accelerometer x', 'Accelerometer y', 'Accelerometer z', 'Temperature'],
                        'ds_ratio': 50,
                        'show': True},
                 "lw": {"axis": ['Accelerometer x', 'Accelerometer y', 'Accelerometer z'],
                        'ds_ratio': 50,
                        'show': False},
                 "ra": {"axis": ['Gyroscope x', 'Gyroscope y', 'Gyroscope z', 'Temperature'],
                        'ds_ratio': 50,
                        'show': True},
                 "la": {"axis": ['Gyroscope x', 'Gyroscope y', 'Gyroscope z'],
                        'ds_ratio': 50,
                        'show': False}
                 }


bout_plot_dict = {'gait_bouts': {'show': True, 'color': 'gold', 'min_dur': 60, 'alpha': .15, 'on_subplot': ['rw', 'ra', 'rw_epoch']},
                  'sleep': {'show': True, 'color': 'purple', 'min_dur': None, 'alpha': .15, 'on_subplot': ['rw', 'rw_epoch']},
                  'rw_nw': {'show': True, 'color': 'grey', 'alpha': .75, 'on_subplot': ['rw', 'rw_epoch']},
                  'lw_nw': {'show': False, 'color': 'grey', 'alpha': .75, 'on_subplot': ['lw', 'lw_epoch']},
                  'ra_nw': {'show': True, 'color': 'grey', 'alpha': .75, 'on_subplot': ['ra']},
                  'la_nw': {'show': False, 'color': 'grey', 'alpha': .75, 'on_subplot': ['la']}}

epoch_plot_dict = {'rw_epoch': {"show": True, 'center': False, 'markers': ['light', 'moderate', 'vigorous', 'mvpa'], 'size': 10}}

plot_data(imu_data=imu_data, tab_data=tab_data, epoch_data=epoch_data,
          imu_plot_dict=imu_plot_dict,
          bout_plot_dict=bout_plot_dict,
          epoch_plot_dict=epoch_plot_dict,
          start_time='2023-02-03 00:00:00', end_time='2023-02-05 00:00:00',
          figsize=(12, 8))