import getopt
import sys

import pandas as pd


def create_file(workload, image, xid, data):
    file_name = f"results/{workload}_{image}_{xid}.tsv"
    with open(file_name, "w") as f:
        f.write(f"{image}\n")
    df = pd.DataFrame(data)
    df.to_csv(f"results/{workload}_{image}_{xid}.tsv", sep="\t", mode="a", index=False)


def parse_results(file_name):
    maketrans = str.maketrans
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

    create_file(workload, image, xid, data)


def main(argv):
    file = ""
    opts, args = getopt.getopt(argv, "f:", ["file="])
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            file = arg

    parse_results(file)


if __name__ == '__main__':
    main(sys.argv[1:])