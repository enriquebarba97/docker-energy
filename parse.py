import getopt
import sys

import pandas as pd



def create_file(workload: str, image: str, samples: str, df: pd.DataFrame):
    file_name = f"results/{workload}_{image}{samples}.tsv"
    with open(file_name, "w") as f:
        f.write(f"{image}\n")
    # df = pd.DataFrame(data)
    df.to_csv(f"results/{workload}_{image}{samples}.tsv", sep="\t", mode="a", index=False)


def parse_results(file_name: str):
    with open(file_name) as f:
        lines = f.readlines()
        data = {"cores (J)": [], "ram (J)": [], "gpu (J)": [], "pkg (J)": [], "time (s)": []}
        workload = ""
        image = ""
        xid = ""

        for line in lines:
            line = line.split()
            if len(line) == 0:
                continue
            if "experiment" in line:
                xid = line[2]
                if len(data["cores (J)"]) > 0:
                    create_file(workload, image, xid, data)
                    data = {k: [] for k in data}
            elif "workload:" in line:
                workload = line[2]
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
    create_file(workload, image, "", df)


def parse_samples(file_name: str):
    with open(file_name) as f:
        lines = f.readlines()
        samples = list()
        data = list()
        headers = list()
        run = list()
        workload = ""
        image = list()
        for line in lines:
            line = line.split()
            if len(line) == 0:
                continue
            elif "workload:" in line:
                workload = line[2]
            elif "image:" in line:
                image = [line[2]]
            elif len(samples) > 0 and "###" in line[0]:
                print("TEST")
                samples = list()
                df = pd.DataFrame(data, columns=headers)
                df["Watts"] = pd.to_numeric(df["Watts"])
                create_file(workload, image, "_samples", df)

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
    run.extend([0.5*i for i in range(len(df["Watts"]))])
    image = image * len(data)
    df = pd.DataFrame([run, data, image])
    df = df.transpose()
    df.columns = ["Time", "Watts", "Image"]

    create_file(workload, image[0], "_samples", df)


def total_order(files: list):
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


def main(argv):
    file = list()
    opts, args = getopt.getopt(argv, "f:", ["file="])
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            file.append(arg)
    if len(file) == 1:
        filename = file[0]
        if "samples" in filename:
            parse_samples(filename)
        else:
            parse_results(filename)
    elif len(file) > 1:
        total_order(file)
    else:
        print("No file provided.")


if __name__ == '__main__':
    main(sys.argv[1:])
