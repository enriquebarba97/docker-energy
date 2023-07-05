import getopt
import sys
import glob
import pandas as pd
import os
from pathlib import Path
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


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

    for image in images:
        files = get_files(f"{directory}/{image}", "*.csv")
        for file in files:
            base, df = read_tsv(file)
            df_delta = df.filter(regex=columns).copy()
            for key in df_delta.keys():
                df_delta[key] = df_delta[key].values.astype(float)
                df_delta[key] = df_delta[key].diff().fillna(0)
            df["TOTAL_POWER (W)"] = (
                df_delta.sum(axis=1).div(df["Delta"], axis=0).fillna(0).multiply(1000)
            )
            df["ELAPSED_TIME (s)"] = df["Delta"].cumsum().div(1000)

            create_file(base, df, f"{directory}/{image}")


def parse_greenserver(directory: str, columns=r"CORE\d+_ENERGY \(J\)"):
    print(directory)
    if not os.path.exists(directory):
        return

    images = [
        image
        for image in os.listdir(directory)
        if os.path.isdir(f"{directory}/{image}")
    ]

    files = get_files(f"{directory}", "*.csv")
    for image in images:
        files = get_files(f"{directory}/{image}", "*.csv")
        if len(files) == 0:
            return

        # Get the column names
        base, df = read_tsv(files[0])
        df_delta = df.filter(regex=columns).copy()
        keys = [key for key in df_delta.keys()]
        keys.sort()

        # Set the headers
        headers = ["ELAPSED_TIME (s)"]
        for key in keys:
            power = f"{key[:-10]}AVERAGE_POWER (W)"
            headers.extend([power, key])

        data = list()
        for file in files:
            run_data = list()
            base, df = read_tsv(file)

            # Calculate the total time
            datetime_start = datetime.strptime(
                df["Time"].iloc[0][:-3], "%Y-%m-%dT%H:%M:%S.%f"
            ).timestamp()
            datetime_end = datetime.strptime(
                df["Time"].iloc[-1][:-3], "%Y-%m-%dT%H:%M:%S.%f"
            ).timestamp()
            total_time = datetime_end - datetime_start
            run_data.append(total_time)

            # For each key, calculate the average power and energy
            for key in keys:
                df[key] = df[key].values.astype(float)
                energy = df[key].iloc[-1] - df[key].iloc[0]
                # print(watts)
                power = (energy / total_time) if total_time != 0 else 0
                run_data.extend([power, energy])

            data.append(run_data)
        df = pd.DataFrame(data, columns=headers)
        create_file(image, df, directory)


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
        sep=",",
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
        parse_greenserver(directory)
    elif mode == "greenserver-samples":
        parse_greenserver(directory)
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
