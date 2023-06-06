import getopt
import sys
import glob
import pandas as pd


def create_file(image: str, df: pd.DataFrame, directory: str = "results"):
    file_name = f"{directory}/{image}.tsv"
    with open(file_name, "w") as f:
        f.write(f"{image}\n")
    # df = pd.DataFrame(data)
    df.to_csv(f"{directory}/{image}.tsv", sep="\t", mode="a", index=False)


def parse_results(file_name: str, directory: str = "results"):
    with open(file_name) as f:
        lines = f.readlines()
        data = {"cores (J)": [], "ram (J)": [], "gpu (J)": [], "pkg (J)": [], "time (s)": []}
        image = ""

        for line in lines:
            line = line.split()
            if len(line) == 0:
                continue
            if "experiment" in line:
                xid = line[2]
                if len(data["cores (J)"]) > 0:
                    df = pd.DataFrame(data)
                    create_file(image, df, directory)
                    data = {k: [] for k in data}
            # elif "workload:" in line:
            #     workload = line[2]
            elif "image:" in line:
                image = line[2]
            elif "run" in line:
                continue
            elif "power/energy-cores/" in line:
                m = line[0].replace('.', '').replace(',', '.')
                data["cores (J)"].append(m)
            elif "power/energy-ram/" in line:
                m = line[0].replace('.', '').replace(',', '.')
                data["ram (J)"].append(m)
            elif "power/energy-gpu/" in line:
                m = line[0].replace('.', '').replace(',', '.')
                data["gpu (J)"].append(m)
            elif "power/energy-pkg/" in line:
                m = line[0].replace('.', '').replace(',', '.')
                data["pkg (J)"].append(m)
            elif "time" in line:
                m = line[0].replace('.', '').replace(',', '.')
                data["time (s)"].append(m)
            else:
                continue

    df = pd.DataFrame(data)
    create_file(image, df, directory)


def parse_samples(file_name: str, directory: str = "results"):
    with open(file_name) as f:
        lines = f.readlines()
        samples = list()
        data = list()
        headers = list()
        run = list()
        image = ""
        for line in lines:
            line = line.split()
            if len(line) == 0:
                continue
            # elif "workload:" in line:
            #     workload = line[2]
            elif "image:" in line:
                image = line[2]
            elif len(samples) > 0 and "###" in line[0]:
                last_run = pd.DataFrame(samples, columns=headers)

                data.extend(pd.to_numeric(last_run["Watts"]).values.tolist())
                run.extend([0.5 * i for i in range(len(data))])
                images = [image] * len(data)
                df = pd.DataFrame([run, data, images])
                df = df.transpose()
                df.columns = ["Time", "Watts", "Image"]

                create_file(image, df, directory)

                samples = list()
                data = list()
                headers = list()
            elif "run" in line and len(samples) > 0:
                df = pd.DataFrame(samples, columns=headers)

                data.extend(pd.to_numeric(df["Watts"]).values.tolist())
                run.extend([0.5*i for i in range(len(df["Watts"]))])

                headers = list()
                samples = list()
            elif len(headers) > 0:
                samples.append(line)
            elif line[0] == "Time":
                headers = line
                samples = list()

    last_run = pd.DataFrame(samples, columns=headers)

    data.extend(pd.to_numeric(last_run["Watts"]).values.tolist())
    run.extend([0.5*i for i in range(len(data))])
    images = [image] * len(data)
    df = pd.DataFrame([run, data, images])
    df = df.transpose()
    df.columns = ["Time", "Watts", "Image"]

    create_file(image, df, directory)


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
    files_samples = list()

    files.extend(glob.glob(f"{directory}/" + f"{extension}"))
    files_samples.extend(glob.glob(f"{directory}/samples/" + f"{extension}"))
    return files, files_samples


def parse_files(files: list, files_samples: list, directory: str):
    for file in files:
        parse_results(file, directory)
    for file in files_samples:
        parse_samples(file, directory+"/samples")


def main(argv):
    files = list()
    files_samples = list()
    directory = "results"
    opts, args = getopt.getopt(argv, "f:d:", ["file=", "directory="])
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            files.append(arg)
        if opt in ["-d", "--directory"]:
            directory = arg
            if directory[-1] == "/":
                directory = directory[:-1]
            files, files_samples = get_files(directory, "*.txt")

    parse_files(files, files_samples, directory)

    # if len(file) == 1:
    #     filename = file[0]
    #     if "samples" in filename:
    #         parse_samples(filename)
    #     else:
    #         parse_results(filename)
    # elif len(file) > 1:
    #     total_order(file)
    # else:
    #     print("No file provided.")


if __name__ == '__main__':
    main(sys.argv[1:])
