import getopt
import sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt

import seaborn as sns
import parse

from pathlib import Path


def get_lists(images: dict):
    # Prepare the lists for the results
    # Labels are the base images
    labels = list(images.keys())
    # Parts are the different measurements (e.g. CPU, GPU, etc.)
    parts = list(images[labels[0]].columns)
    return labels, parts


def shapiro_test(images: dict, labels: list, parts: list):
    print(
        "============================== Shapiro-Wilk test =============================="
    )
    print(
        "True means that the null hypothesis is rejected, i.e. the data is not normal.\n"
    )
    # normal = list()
    # Perform the Shapiro-Wilk test for normality for each part of each base image
    for label in labels:
        header = ["part", "reject", "p-value"]
        data = list()
        print(f"{label}:")
        for part in parts:
            x = images[label][part].values.astype(float)
            # print(list(x))
            shapiro, p = stats.shapiro(list(x))
            r = False
            # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the data is not normal)
            if p < 0.05:
                r = True
            data.append([part, r, p])
            # print(f"\t {part}: {str(r)} - {p}")
        # normal.append(n)
        print(f"{pd.DataFrame(data, columns=header)}\n")
    # return labels, normal


def anova_test(images: dict, labels: list, parts: list):
    print(
        "============================== One-way ANOVA test ============================="
    )

    if len(labels) < 2:
        print("Not enough data to perform the test.")
        return

    print(
        "True means that the null hypothesis is rejected, i.e. the means are not equal.\n"
    )

    print(f"One-way ANOVA test between {', '.join(labels)}:")
    header = ["part", "reject", "p-value"]
    data = list()
    # Perform the one-way ANOVA test for each part between the base images
    for part in parts:
        x = list()
        r = False
        for label in labels:
            x.append(images[label][part].values.astype(float))
        _, p = stats.f_oneway(*x)
        # print(p)
        # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the means are not equal)
        if p < 0.05:
            r = True
        data.append([part, r, p])
        # print("\t" + part + ": " + str(s))
        # print(p)
    print(pd.DataFrame(data, columns=header))
    # return parts, significance


def tukey_test(images: dict, labels: list, parts: list):
    print(
        "============================== Tukey HSD test ================================="
    )

    if len(labels) < 2:
        print("Not enough data to perform the test.")
        return

    print("False means that the null hypothesis is rejected, i.e. the means are equal.")
    # tukey = list()
    # Perform the Tukey HSD test for each part between the base images
    for part in parts:
        scores = list()
        print(f"Tukey HSD test for {part}:")
        try:
            for label in labels:
                scores.extend(images[label][part].values.astype(float))
            df = pd.DataFrame(
                {
                    "score": scores,
                    "group": np.repeat(labels, repeats=len(scores) / len(labels)),
                }
            )
            t = pairwise_tukeyhsd(endog=df["score"], groups=df["group"], alpha=0.05)
            print(f"{t}\n")
        except KeyError as e:
            print(
                f"{e} cannot be compared since it is not present in all the dataframes."
            )
            continue
        # tukey.append(t)
        # print(part + ":")
        # print(t)
    # return parts, tukey


def calculate_d(x, y):
    # Compute the Cohen's d effect size
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(
        ((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof
    )


def cohen_d(images: dict, labels: list, parts: list):
    print(
        "============================== Cohen's d test ================================="
    )

    if len(labels) < 2:
        print("Not enough data to perform the test.")
        return
    
    print(
        "A positive value indicates that the second image performs better than the first.\n"
    )
    # cohen = list()
    # Perform the Cohen's d test for each part between the base images
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            header = ["part", "d"]
            data = list()
            print("Cohen's d effect size for " + labels[i] + " and " + labels[j] + ":")
            for part in parts:
                d = calculate_d(
                    images[labels[i]][part].values.astype(float),
                    images[labels[j]][part].values.astype(float),
                )
                data.append([part, d])
                # print("\t" + part + ": " + str(d))
            # cohen.append(c)
            print(f"{pd.DataFrame(data, columns=header)}\n")

    # return parts, cohen


def statistics(images: dict, labels: list, parts: list):
    for label in labels:
        print(f"{label} (mean; standard deviation):")
        for part in parts:
            print(
                f"\t{part}: {np.mean(images[label][part].values.astype(float))}; "
                f"{np.std(images[label][part].values.astype(float))}"
            )


def plot(images: dict, labels: list, parts: list):
    for part in parts:
        compare = list()
        for label in labels:
            compare.append(images[label][part].values.astype(float))
        plt.figure(figsize=(10, 7))
        # plt.boxplot(compare)
        # plt.violinplot(compare)
        sns.boxplot(data=compare)
        plt.xticks(range(0, len(labels)), labels)
        plt.title(part)
        plt.show()


def plot_samples(images: dict, x_value: str, y_value: str):
    sns.set_style("whitegrid")
    df = pd.DataFrame()
    for image in images:
        if df.empty:
            df = images[image]
        else:
            df = pd.concat([df, images[image]], ignore_index=True)

    try:
        plt.figure(figsize=(10, 7))
        sns.lineplot(x=x_value, y=y_value, data=df, hue="Run")

        plt.title("Power usage over time")
        plt.show()
    except:
        print("Incorrect values for x and y")


def analyze(images: dict, images_samples: dict, labels: list, parts: list):
    normal = shapiro_test(images, labels, parts)
    significance = anova_test(images, labels, parts)
    tukey = tukey_test(images, labels, parts)
    cohen = cohen_d(images, labels, parts)
    plot(images, labels, parts)
    return normal, significance, tukey, cohen


def read_tsv(file: str):
    base = Path(file).stem
    with open(file) as f:
        # Read the first line for the base image name
        # base = f.readline().rstrip().split("\t")[0]
        # Read the second line for the column names
        parts = f.readline().rstrip().split("\t")
        data = f.readline().rstrip().split("\t")
        if len(data) != len(parts):
            raise ValueError(
                "The header length in the file does not match the number of columns."
            )
    return base, pd.read_csv(file, sep="\t", skiprows=1, names=parts)


def parse_args(argv):
    files = list()
    parts = list()
    statistical_test = list()
    x_value = ""
    y_value = ""

    # Get the arguments provided by the user
    opts, args = getopt.getopt(
        argv,
        "f:d:p:x:y:",
        [
            "file=",
            "directory=",
            "part=",
            "shapiro",
            "anova",
            "tukey",
            "cohen",
            "full",
            "statistics",
            "plot",
            "plot-samples",
        ],
    )
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            files.append(arg)
        if opt in ["-d", "--directory"]:
            directory = arg
            if directory[-1] == "/":
                directory = directory[:-1]
            files = parse.get_files(directory, "*.tsv")
        elif opt in ["-p", "--part"]:
            parts.append(arg)
        elif opt == "--shapiro":
            statistical_test.append("shapiro")
        elif opt == "--anova":
            statistical_test.append("anova")
        elif opt == "--tukey":
            statistical_test.append("tukey")
        elif opt == "--cohen":
            statistical_test.append("cohen")
        elif opt == "--full":
            statistical_test.append("full")
        elif opt == "--statistics":
            statistical_test.append("statistics")
        elif opt == "--plot":
            statistical_test.append("plot")
        elif opt == "--plot-samples":
            statistical_test.append("plot-samples")
        elif opt == "-x":
            x_value = arg
        elif opt == "-y":
            y_value = arg

    return files, parts, statistical_test, x_value, y_value


def main(argv):
    images = {}
    images_samples = {}
    files, parts, statistical_test, x_value, y_value = parse_args(argv)

    # if len(files) == 0:
    #     print("No .tsv files provided")
    #     return

    # Read the TSV files
    for f in files:
        try:
            base, df = read_tsv(f)
            images[base] = df
        except ValueError as e:
            print(f"{f}: {e}")

    if len(images) == 0:
        print("No (correct) .tsv files provided")
        return

    labels, all_parts = get_lists(images)

    for p in parts:
        if p not in all_parts:
            print(
                f"Part {p} not found in the data; choose one from: {', '.join(all_parts)}"
            )
            return

    if len(parts) == 0:
        parts = all_parts

    # labels = list(images.keys())

    if len(statistical_test) == 0:
        print("No statistical test selected.")
        return
    if "full" in statistical_test:
        analyze(images, images_samples, labels, parts)
        return
    if "shapiro" in statistical_test:
        shapiro_test(images, labels, parts)
    if "anova" in statistical_test:
        anova_test(images, labels, parts)
    if "tukey" in statistical_test:
        tukey_test(images, labels, parts)
    if "cohen" in statistical_test:
        cohen_d(images, labels, parts)
    if "statistics" in statistical_test:
        statistics(images, labels, parts)
    if "plot" in statistical_test:
        plot(images, labels, parts)
    elif "plot-samples" in statistical_test:
        plot_samples(images, x_value, y_value)


if __name__ == "__main__":
    main(sys.argv[1:])
