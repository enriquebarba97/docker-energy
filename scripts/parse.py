import getopt
import sys
import glob
import pandas as pd
import os
from pathlib import Path
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import seaborn as sns


def create_file(file_name: str, df: pd.DataFrame, directory: str):
    # image = image.replace(":", "")
    # file_name = f"{directory}/{image}-{run}.tsv"
    # with open(file_name, "w") as f:
    #     f.write(f"{image}\n")
    # df = pd.DataFrame(data)
    df.to_csv(f"{directory}/{file_name}.tsv", sep="\t", index=False)  # , mode="a")


def parse_results_perf(file_name: str, directory: str = "results"):
    image = Path(file_name).stem
    with open(file_name) as f:
        lines = f.readlines()
        data = {
            "time (s)": [],
            # "cores (J)": [],
            # "ram (J)": [],
            # "gpu (J)": [],
            "pkg (J)": [],
        }
        # image = ""

        for line in lines:
            line = line.split()
            if len(line) == 0:
                continue
            if "experiment" in line:
                xid = line[2]
                if len(data["time (s)"]) > 0:
                    df = pd.DataFrame(data)
                    create_file(image, df, directory)
                    data = {k: [] for k in data}
            # elif "workload:" in line:
            #     workload = line[2]
            # elif "image:" in line:
            #     image = line[2]
            elif "run" in line:
                continue
            elif "power/energy-cores/" in line:
                m = line[0].replace(".", "").replace(",", ".")
                data["cores (J)"].append(m)
            elif "power/energy-ram/" in line:
                m = line[0].replace(".", "").replace(",", ".")
                data["ram (J)"].append(m)
            elif "power/energy-gpu/" in line:
                m = line[0].replace(".", "").replace(",", ".")
                data["gpu (J)"].append(m)
            elif "power/energy-pkg/" in line:
                m = line[0].replace(".", "").replace(",", ".")
                data["pkg (J)"].append(m)
            elif "time" in line:
                m = line[0].replace(".", "").replace(",", ".")
                data["time (s)"].append(m)
            else:
                continue

    try:
        df = pd.DataFrame(data)
        create_file(image, df, directory)
    except:
        print(f"Incorrect file")


def parse_results_perf_samples(directory: str):
    if not os.path.exists(directory):
        return

    images = [
        image
        for image in os.listdir(directory)
        if os.path.isdir(f"{directory}/{image}")
    ]

    for image in images:
        files = get_files(f"{directory}/{image}", "*.tsv")
        data = list()
        for file in files:
            base, df = read_tsv(file)
            energy = df["Energy"].sum()
            time = df["Time"].iloc[-1]
            data.append([time, energy])
        df = pd.DataFrame(data, columns=["Time", "Energy"])
        create_file(image, df, directory)


def parse_greenserver_samples(directory: str, columns=r"CORE\d+_ENERGY \(J\)"):
    if not os.path.exists(directory):
        return

    images = [
        image
        for image in os.listdir(directory)
        if os.path.isdir(f"{directory}/{image}")
    ]
    print(directory)

    for image in images:
        # if image != "centoslatest":
        #     continue
        print(directory)
        files = get_files(f"{directory}/{image}", "*.tsv")
        print(image)
        df_avg = pd.DataFrame()
        df_time = pd.DataFrame()
        cores = [0]
        cpus = [0, 12]
        largest = 0
        x = 0
        for file in files:
            base, df = read_tsv(file)
            # print(base)

            for key in df.keys():
                try:
                    df[key] = df[key].values.astype(float)
                except:
                    continue
            df_samples = pd.DataFrame()
            df_samples = get_greenserver_time(df_samples, df)
            df_samples = get_greenserver_average_power(df_samples, df, cores)
            df_samples = get_greenserver_cpu_usage(df_samples, df, cpus)
            if len(df_samples[f"CORE0_AVERAGE_POWER (W)"]) > largest:
                largest = len(df_samples[f"CORE0_AVERAGE_POWER (W)"])
                x = base
                df_time = get_greenserver_time(pd.DataFrame(), df)
                # print(df_time)
            if df_avg.empty:
                df_avg = df_samples
            else:
                df_avg = df_avg.add(df_samples, fill_value=0)
            # df = get_greenserver_cpu_usage(df, [0, 12])
        df_avg = df_avg / 30
        df_avg = pd.concat([df_time, df_avg], axis=1)
        print(df_avg)

        sns.set_style("white")
        plt.figure(figsize=(10, 7))

        x_value = "INTERVAL_ELAPSED_TIME (s)"
        y_value1 = f"CORE0_AVERAGE_POWER (W)"
        y_value2 = f"CPU0_USAGE_DELTA"
        ax = sns.lineplot(
            x=x_value,
            y=y_value1,
            data=df_avg,
            # color="b",
        )
        # sns.lineplot(
        #     x=x_value,
        #     y="CPU12_USAGE_DELTA",
        #     data=df_avg,
        #     color="g",
        # )
        # ax = sns.lineplot(
        #     x=x_value,
        #     y=y_value1,
        #     data=df_avg,
        # )
        # ax = sns.lineplot(
        #     x=x_value,
        #     y="CPU12_USAGE_DELTA",
        #     data=df_avg,
        # )
        # ax2 = ax.twinx()
        # sns.lineplot(
        #     x=x_value,
        #     y=y_value2,
        #     data=df_avg,
        #     ax=ax2,
        #     color="g",
        # )
        # ax.legend(
        #     handles=[
        #         # Line2D([], [], marker="_", color="b", label="CORE0_AVERAGE_POWER (W)"),
        #         Line2D([], [], marker="_", color="g", label="CPU0_USAGE_DELTA"),
        #         Line2D([], [], marker="_", color="b", label="CPU12_USAGE_DELTA"),
        #     ]
        # )
        # ax.set(xlim=(0, 200), ylim=(0, 16))
        # ax.set(xlim=(0, 200))
        # plt.title(f"Power over time ({image})")
        # plt.title(f"CPU usage over time ({image})")
        # plt.show()
        print(df_samples)


def get_greenserver_average_power(
    df_samples: pd.DataFrame, df: pd.DataFrame, cpus: list
):
    df_delta = df.filter(regex=r"CORE\d+_ENERGY \(J\)").copy()

    if "GPU_POWER (W)" in df:
        df_samples[f"GPU_AVERAGE_POWER (W)"] = (
            df[f"GPU_POWER (W)"]
            .div(df_samples["TIME_DELTA (s)"], axis=0)
            .replace([np.inf, -np.inf], 0)
            .fillna(0)
            # .multiply(1000)
        )
        # print(np.trapz(df[f"GPU_POWER (W)"], df_samples["ELAPSED_TIME (s)"]))
        # print(
        #     df_samples[f"GPU_AVERAGE_POWER (W)"].mean()
        #     / ((df_samples["ELAPSED_TIME (s)"].max() * 10))
        # )
    for cpu in cpus:
        diff = 0
        i = df_delta[f"CORE{cpu}_ENERGY (J)"].lt(0).idxmax()
        if i > 0:
            diff = abs(
                df_delta[f"CORE{cpu}_ENERGY (J)"].iloc[i - 1]
                - abs(df_delta[f"CORE{cpu}_ENERGY (J)"].iloc[i])
            )
        df_delta[f"CORE{cpu}_ENERGY (J)"] = (
            df_delta[f"CORE{cpu}_ENERGY (J)"].diff().fillna(0)
        )

        if diff > 0:
            df_delta[f"CORE{cpu}_ENERGY (J)"].at[i] = diff

        df_samples[f"CORE{cpu}_AVERAGE_POWER (W)"] = (
            df_delta[f"CORE{cpu}_ENERGY (J)"]
            .div(df_samples["TIME_DELTA (s)"], axis=0)
            .fillna(0)
            # .multiply(1000)
        )

        df_samples[f"CORE{cpu}_ENERGY_SAMPLE (J/interval)"] = (
            df_delta[f"CORE{cpu}_ENERGY (J)"]
            # .div(df_samples["TIME_DELTA (s)"], axis=0)
            # .fillna(0)
            # .multiply(1000)
        )
        df_samples[f"CORE{cpu}_ENERGY_SAMPLE_DIFF"] = (
            df_samples[f"CORE{cpu}_ENERGY_SAMPLE (J/interval)"]
            .diff()
            .fillna(0)
            .div(df_samples["TIME_DELTA (s)"], axis=0)
            .fillna(0)
        )
        df_samples[f"CORE{cpu}_AVERAGE_POWER (W)"].replace(
            [np.inf, -np.inf], 0, inplace=True
        )
    # df_samples["TOTAL_AVERAGE_POWER (W)"] = (
    #     df_delta.sum(axis=1).div(df["Delta"], axis=0).fillna(0).multiply(1000)
    # )
    return df_samples


def get_greenserver_cpu_usage(df_samples: pd.DataFrame, df: pd.DataFrame, cpus: list):
    df_cpus = df.filter(regex=r"CPU\d+_USAGE \(%\)").copy()
    for cpu in cpus:
        df_samples[f"CPU{cpu}_USAGE_DELTA"] = (
            df_cpus[f"CPU{cpu}_USAGE (%)"].diff().fillna(0)
        )
    return df_samples


def get_greenserver_time(df_samples: pd.DataFrame, df: pd.DataFrame):
    df_delta = df.filter(regex=r"Time").copy()
    df_delta["TIME_NEW"] = pd.to_datetime(df_delta["Time"])
    df_delta["TIME_OLD"] = pd.to_datetime(df_delta["Time"].shift(1).fillna(0))
    df_delta["TIME_OLD"].at[0] = df_delta["TIME_NEW"].at[0]
    df_samples["TIME_DELTA (s)"] = (
        df_delta["TIME_NEW"] - df_delta["TIME_OLD"]
    ).dt.total_seconds()
    # df_samples["TIME_DELTA (s)"] = df_delta["TIME_DELTA (s)"]
    df_samples["INTERVAL_ELAPSED_TIME (s)"] = df["Delta"].cumsum() / 1000
    df_samples["ELAPSED_TIME (s)"] = df_samples["TIME_DELTA (s)"].cumsum()
    return df_samples


def parse_greenserver(directory: str, columns=r"CORE\d+_ENERGY \(J\)"):
    print(directory)
    if not os.path.exists(directory):
        return

    images = [
        image
        for image in os.listdir(directory)
        if os.path.isdir(f"{directory}/{image}")
    ]

    for image in images:
        files = get_files(f"{directory}/{image}", "*.tsv")
        if len(files) == 0:
            return

        # Get the column names
        base, df = read_tsv(files[0])
        df_delta = df.filter(regex=columns).copy()
        keys = [key for key in df_delta.keys()]
        keys.sort()

        # Set the headers
        headers = ["RUN", "TIME (s)"]
        for key in keys:
            power = f"{key[:-10]}AVERAGE_POWER (W)"
            headers.extend([power, key])
        headers.extend(["TOTAL_CORE_AVERAGE_POWER (W)", "TOTAL_CORE_ENERGY (J)"])
        # if "GPU_POWER (W)" in df:
        #     headers.extend(["GPU_ENERGY (J)"])
        headers.extend(["ENERGY (J)"])

        data = list()
        for file in files:
            run_data = list()
            base, df = read_tsv(file)
            run_data.append(int(base[4:]))

            # Calculate the total time
            datetime_start = datetime.strptime(
                df["Time"].iloc[0][:-3], "%Y-%m-%dT%H:%M:%S.%f"
            ).timestamp()
            datetime_end = datetime.strptime(
                df["Time"].iloc[-1][:-3], "%Y-%m-%dT%H:%M:%S.%f"
            ).timestamp()

            df_samples = pd.DataFrame()
            df_samples = get_greenserver_time(df_samples, df)

            total_time = datetime_end - datetime_start
            run_data.append(total_time)

            # For each key, calculate the average power and energy, and the total values
            total_energy = 0
            total_power = 0
            run_energy = 0
            for key in keys:
                df[key] = df[key].values.astype(float)
                energy = df[key].iloc[-1] - df[key].iloc[0]
                # If the energy is negative, it means that the counter has overflowed
                if energy < 0:
                    # Get the first negative value
                    i = df[key].lt(0).idxmax()
                    # Calculate the difference between the last positive value and the first negative value
                    switch_diff = abs(df[key].iloc[i - 1] - abs(df[key].iloc[i]))
                    # Calculate the difference between the first value and the last positive value
                    positive_diff = df[key].iloc[i - 1] - df[key].iloc[0]
                    # Calculate the difference between the last value and the first negative value
                    negative_diff = df[key].iloc[-1] - df[key].iloc[i]
                    energy = switch_diff + positive_diff + negative_diff
                power = (energy / total_time) if total_time != 0 else 0
                run_data.extend([power, energy])
                total_energy += energy
                total_power += power
                if key == "CORE0_ENERGY (J)":
                    run_energy = energy

            run_data.extend([total_power, total_energy])
            # if "GPU_POWER (W)" in df:
            #     df[f"GPU_POWER (W)"] = df[f"GPU_POWER (W)"].values.astype(float)
            #     gpu_energy = np.trapz(
            #         df[f"GPU_POWER (W)"], df_samples["ELAPSED_TIME (s)"]
            #     )
            #     run_data.extend([gpu_energy])
            #     run_energy += gpu_energy
            run_data.extend([run_energy])
            data.append(run_data)
        df = pd.DataFrame(data, columns=headers)
        # print(df)
        create_file(
            image,
            df.sort_values(by=["RUN"], ascending=True).reset_index(drop=True),
            directory,
        )


def parse_results_samples(file_name: str, directory: str = "results"):
    with open(file_name) as f:
        lines = f.read().splitlines()
        samples = list()
        data = list()
        headers = list()
        run = -1
        image = ""
        start = False
        results = False
        experiment_info = ["### experiment", "# cpus:", "# workload:", "# started on"]
        for line in lines:
            if len(line.split()) == 0:
                continue
            elif any([x in line for x in experiment_info]):
                continue
            elif "# image:" in line:
                image = line.split()[2]
            elif "# run" in line:
                results = False
                start = True
                run = line.split()[2][:-1]
            elif start:
                if results:
                    line = line.split(",")
                    line.insert(0, run)
                    samples.append(line)
                elif len(headers) == 0:
                    headers = line.split(",")
                    headers.insert(0, "Run")
                    results = True
                else:
                    results = True

    try:
        df = pd.DataFrame(samples, columns=headers)
        create_file(image, df, directory)
    except:
        print(f"Incorrect file")


def total_order(files: list, directory: str = "results"):
    data = list()
    for file in files:
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                line = line.split()
                if "run" in line:
                    data.append((int(line[2][:-2]), line[5]))
    df = pd.DataFrame(data, columns=["run", "image"])
    df = df.sort_values(by=["run"], ascending=True)
    df.to_csv("total_order.tsv", sep="\t", mode="a", index=False)


def read_tsv(file: str):
    base = Path(file).stem
    return base, pd.read_csv(
        file,
        sep="\t",
        # skiprows=1,
        # header=None,
        # usecols=[0, 1],
        # names=["Time", "Energy"],
        decimal=",",
    )


def get_files(directory: str, extension: str):
    files = list()
    files.extend(glob.glob(f"{directory}/" + f"{extension}"))
    return files


def parse_files(mode: str, files: list, directory: str):
    for file in files:
        parse_results(file, directory)
    if mode == "perf":
        for file in files:
            parse_results_perf(file, directory)
    elif mode == "perf-samples":
        parse_results_perf_samples(directory)
    elif mode == "samples":
        for file in files:
            parse_results_samples(file, directory)
    elif mode == "greenserver":
        workloads = [
            workload
            for workload in os.listdir(directory)
            if os.path.isdir(f"{directory}/{workload}")
        ]
        for workload in workloads:
            # if workload != "llama.cpp-gpu":
            #     continue
            parse_greenserver(f"{directory}/{workload}")
    elif mode == "greenserver-samples":
        workloads = [
            workload
            for workload in os.listdir(directory)
            if os.path.isdir(f"{directory}/{workload}")
        ]
        for workload in workloads:
            if workload != "llama.cpp-gpu":
                continue
            parse_greenserver_samples(f"{directory}/{workload}")
        # parse_greenserver_samples(f"{directory}")
    else:
        print("No mode selected")


def main(argv):
    files = list()
    directory = "results"
    mode = ""
    opts, args = getopt.getopt(
        argv,
        "f:d:",
        [
            "file=",
            "directory=",
            "perf",
            "perf-samples",
            "samples",
            "greenserver",
            "greenserver-samples",
        ],
    )
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            files.append(arg)
        elif opt in ["-d", "--directory"]:
            directory = arg
            if directory[-1] == "/":
                directory = directory[:-1]
            # files = get_files(directory, "*.txt")
        elif opt == "--perf":
            mode = "perf"
        elif opt == "--perf-samples":
            mode = "perf-samples"
        elif opt == "--samples":
            mode = "samples"
        elif opt == "--greenserver":
            mode = "greenserver"
        elif opt == "--greenserver-samples":
            mode = "greenserver-samples"

    parse_files(mode, files, directory)


if __name__ == "__main__":
    main(sys.argv[1:])
