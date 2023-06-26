import getopt
import sys
import glob
import pandas as pd
from pathlib import Path


def create_file(image: str, df: pd.DataFrame, directory: str = "results"):
    image = image.replace(":", "")
    file_name = f"{directory}/{image}.tsv"
    # with open(file_name, "w") as f:
    #     f.write(f"{image}\n")
    # df = pd.DataFrame(data)
    df.to_csv(f"{directory}/{image}.tsv", sep="\t", mode="a", index=False)


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


def get_files(directory: str, extension: str):
    files = list()
    files.extend(glob.glob(f"{directory}/" + f"{extension}"))
    return files


def parse_files(mode: str, files: list, directory: str):
    # for file in files:
    #     parse_results(file, directory)
    if mode == "perf":
        for file in files:
            parse_results_perf(file, directory)
    elif mode == "samples":
        for file in files:
            parse_results_samples(file, directory)
    else:
        print("No mode selected")


def main(argv):
    files = list()
    directory = "results"
    mode = ""
    opts, args = getopt.getopt(argv, "f:d:", ["file=", "directory=", "perf", "samples"])
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            files.append(arg)
        elif opt in ["-d", "--directory"]:
            directory = arg
            if directory[-1] == "/":
                directory = directory[:-1]
            files = get_files(directory, "*.txt")
        elif opt == "--perf":
            mode = "perf"
        elif opt == "--samples":
            mode = "samples"

    parse_files(mode, files, directory)



if __name__ == "__main__":
    main(sys.argv[1:])
