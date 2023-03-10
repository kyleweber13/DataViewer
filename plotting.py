import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import dates as mdates
xfmt = mdates.DateFormatter("%Y/%m/%d\n%H:%M:%S")
from datetime import timedelta
from utilities import index_from_timestamp


def plot_data(imu_data: dict,
              tab_data: dict,
              epoch_data: dict,
              imu_plot_dict: dict,
              bout_plot_dict: dict,
              epoch_plot_dict: dict,
              start_time: pd.Timestamp or str or None = None,
              end_time: pd.Timestamp or str or None = None,
              figsize: list or tuple = (12, 8),
              ):

    ax_keys = {}

    # keys for IMU(s) to plot
    use_imu_keys = [key for key in imu_plot_dict.keys() if imu_plot_dict[key]['show']]

    # keys for bout data to plot
    use_bout_keys = [key for key in bout_plot_dict.keys() if bout_plot_dict[key]['show']]

    # keys for epoched data to plot
    use_epoch_keys = [key for key in epoch_plot_dict.keys() if epoch_plot_dict[key]['show']]

    # number of subplots
    n_rows = len(use_imu_keys) + len(use_epoch_keys)

    # extra plot if showing temperature
    if True in ['Temperature' in imu_plot_dict[key]['axis'] for key in use_imu_keys]:
        n_rows += 1
        ax_keys['Temperature'] = -1

    fig, ax = plt.subplots(nrows=n_rows, sharex='col', figsize=figsize)

    chn_colors = {"x": 'black', 'y': 'red', 'z': 'dodgerblue'}
    dev_colors = {'rw': 'black', 'lw': 'red', 'la': 'purple', 'ra': 'dodgerblue'}

    # IMU data -------------------------------------------------------------
    for ax_i, key in enumerate(use_imu_keys):
        print(key)
        for chn in imu_plot_dict[key]['axis']:
            print(f"    -{chn}")
            ax[ax_i].set_ylabel(key)

            chn_i = imu_data[key].get_signal_index(chn)

            start_i = index_from_timestamp(timestamp=start_time,
                                           start_timestamp=imu_data[key].ts[0],
                                           sample_rate=imu_data[key].signal_headers[chn_i]['sample_rate']) if \
                start_time is not None else 0

            end_i = index_from_timestamp(timestamp=end_time,
                                         start_timestamp=imu_data[key].ts[0],
                                         sample_rate=imu_data[key].signal_headers[chn_i]['sample_rate']) if \
                end_time is not None else -1

            if 'Accelerometer' in chn or 'Gyroscope' in chn:

                ax[ax_i].plot(imu_data[key].ts[start_i:end_i:imu_plot_dict[key]['ds_ratio']],
                              imu_data[key].signals[chn_i][start_i:end_i:imu_plot_dict[key]['ds_ratio']],
                              color=chn_colors[chn[-1]], label=chn)

            if 'Temperature' in chn:
                ax[ax_keys['Temperature']].plot(imu_data[key].temp_ts[start_i:end_i],
                                                imu_data[key].signals[chn_i][start_i:end_i],
                                                label=key, color=dev_colors[key])
                ax[ax_keys['Temperature']].set_ylabel("Temperature")

        ax_keys[key] = ax_i

    # Epoched data ---------------------------------------------------------

    start_ax_i = max(ax_keys.values()) + 1
    intensity_marker_colors = {"sedentary": 'grey', 'sedentary_gait': 'purple', 'light': 'limegreen',
                               'moderate': 'orange', 'vigorous': 'red', 'none': 'white'}

    for ax_i, key in enumerate(use_epoch_keys):
        print(key)

        df = epoch_data[key].copy()

        if start_time is not None:
            df = df.loc[df['start_time'] >= pd.to_datetime(start_time)]
        if end_time is not None:
            if 'end_time' in df.columns:
                df = df.loc[df['end_time'] <= pd.to_datetime(end_time)]
            if 'end_time' not in df.columns:
                df = df.loc[df['start_time'] <= pd.to_datetime(end_time)]

        if 'start_time' in df.columns and 'end_time' in df.columns:
            epoch_len = (df.iloc[0]['end_time'] - df.iloc[0]['start_time']).total_seconds()

            if 'center' in epoch_plot_dict[key].keys():
                if epoch_plot_dict[key]['center']:
                    df['start_time_mid'] = df['start_time'] + timedelta(seconds=epoch_len/2)
                    time_col = 'start_time_mid'
                    print(f"    -Epoch length = {epoch_len:.0f} seconds (centered)")

                if not epoch_plot_dict[key]['center']:
                    time_col = 'start_time'
                    print(f"    -Epoch length = {epoch_len:.0f} seconds (not centered)")

            if 'center' not in epoch_plot_dict[key].keys():
                time_col = 'start_time'
                print(f"    -Epoch length = {epoch_len:.0f} seconds (not centered)")

        if 'end_time' not in df.columns:
            time_col = 'start_time'
            print("    -Epoch length = 1 second")

        ax[ax_i + start_ax_i].plot(df[time_col], df['avm'],
                                   color='black', label=key, zorder=0)
        ax[ax_i + start_ax_i].set_ylabel(key)
        ax[ax_i + start_ax_i].set_ylim(0, )

        if 'markers' in epoch_plot_dict[key].keys():
            print(f"    -Markers for {epoch_plot_dict[key]['markers']} "
                  f"intensit{'y' if len(epoch_plot_dict[key]['markers']) == 1 else 'ies'}")
            for intensity in epoch_plot_dict[key]['markers']:
                df_intensity = df.loc[df['intensity'] == intensity]

                try:
                    ax[ax_i + start_ax_i].scatter(df_intensity[time_col].iloc[0], df_intensity['avm'].iloc[0],
                                                  color=intensity_marker_colors[intensity],
                                                  s=epoch_plot_dict[key]['size'],
                                                  label=intensity)

                    ax[ax_i + start_ax_i].scatter(df_intensity[time_col].iloc[1:], df_intensity['avm'].iloc[1:],
                                                  color=intensity_marker_colors[intensity],
                                                  s=epoch_plot_dict[key]['size'])
                except IndexError:
                    print(f"        -No data for '{intensity}'")

        ax_keys[key] = ax_i + start_ax_i

    # Bout data ------------------------------------------------------------

    for key in use_bout_keys:
        print(key)

        for subplot in bout_plot_dict[key]['on_subplot']:
            if subplot not in ax_keys.keys():
                print(f"    -Cannot plot on '{subplot}' axis (does not exist)")

            if subplot in ax_keys.keys():
                df = tab_data[key]

                if start_time is not None:
                    df = df.loc[df['start_time'] >= pd.to_datetime(start_time)]
                if end_time is not None:
                    if 'end_time' in df.columns:
                        df = df.loc[df['end_time'] <= pd.to_datetime(end_time)]
                    if 'end_time' not in df.columns:
                        df = df.loc[df['start_time'] <= pd.to_datetime(end_time)]

                if 'min_dur' in bout_plot_dict[key].keys():

                    if 'duration' in df.columns and bout_plot_dict[key]['min_dur'] is not None:
                        df = df.loc[df['duration'] >= bout_plot_dict[key]['min_dur']]
                        print(f"    -Plotting {key} with duration >= {bout_plot_dict[key]['min_dur']} "
                              f"on '{subplot}' axis ({df.shape[0]} bouts)")

                    if 'duration' in df.columns and bout_plot_dict[key]['min_dur'] is None:
                        print("    -Cannot use min_dur (given as None)")

                    if 'duration' not in df.columns:
                        print("    -Cannot use min_dur (no 'duration' column)")

                # first bout for legend label
                if df.shape[0] >= 1:
                    ax[ax_keys[subplot]].axvspan(xmin=df.iloc[0]['start_time'], xmax=df.iloc[0]['end_time'],
                                                 ymin=0, ymax=1,
                                                 label=key,
                                                 color=bout_plot_dict[key]['color'], alpha=bout_plot_dict[key]['alpha'])

                # subsequent bout(s), no label
                if df.shape[0] >= 2:
                    for row in df.iloc[1:].itertuples():
                        ax[ax_keys[subplot]].axvspan(xmin=row.start_time, xmax=row.end_time,
                                                     ymin=0, ymax=1,
                                                     color=bout_plot_dict[key]['color'],
                                                     alpha=bout_plot_dict[key]['alpha'])

    # Final formatting -----------------------------------------------------

    for ax_i in range(n_rows):
        ax[ax_i].legend(loc='lower right')

    ax[-1].xaxis.set_major_formatter(xfmt)
    plt.tight_layout()
