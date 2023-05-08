import getopt
import sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def get_lists(images: dict):
    # Prepare the lists for the results
    # Labels are the base images
    labels = list(images.keys())
    # Parts are the different measurements (e.g. CPU, GPU, etc.)
    parts = list(images[labels[0]].columns)
    return labels, parts


def shapiro_test(images: dict, labels: list, parts: list):
    print("False means that the null hypothesis is rejected, i.e. the data is not normal.")
    normal = list()
    # Perform the Shapiro-Wilk test for normality for each part of each base image
    for label in labels:
        n = list()
        print(label + ": " + str(n))
        print("Shapiro-Wilk test for " + label + ":")
        for part in parts:
            x = images[label][part].values.astype(float)
            shapiro = stats.shapiro(x)
            r = True
            # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the data is not normal)
            if shapiro.pvalue < 0.05:
                r = False
            n.append(r)
            print("\t" + part + ": " + str(r))
        normal.append(n)
    return labels, normal


def anova_test(images: dict, labels: list, parts: list):
    print("False means that the null hypothesis is rejected, i.e. the means are not equal.")
    print(f"One-way ANOVA test between {labels}:")
    significance = list()
    # Perform the one-way ANOVA test for each part between the base images
    for part in parts:
        x = list()
        s = True
        for label in labels:
            x.append(images[label][part].values.astype(float))
        anova = stats.f_oneway(*x)
        # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the means are not equal)
        if anova.pvalue < 0.05:
            s = False
        significance.append(s)
        print("\t" + part + ": " + str(s))
    return parts, significance


def tukey_test(images: dict, labels: list, parts: list):
    print("False means that the null hypothesis is rejected, i.e. the means are equal.")
    tukey = list()
    # Perform the Tukey HSD test for each part between the base images
    for part in parts:
        scores = list()
        for label in labels:
            scores.extend(images[label][part].values.astype(float))
        df = pd.DataFrame({'score': scores,
                           'group': np.repeat(labels, repeats=len(scores) / len(labels))})
        t = pairwise_tukeyhsd(endog=df['score'],
                              groups=df['group'],
                              alpha=0.05)
        tukey.append(t)
        print(part + ":")
        print(t)
    return parts, tukey


def calculate_d(x, y):
    # Compute the Cohen's d effect size
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(
        ((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof)


def cohen_d(images: dict, labels: list, parts: list):
    print("A positive value indicates that the second image performs better than the first.")
    cohen = list()
    # Perform the Cohen's d test for each part between the base images
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            c = list()
            print("Cohen's d effect size for " + labels[i] + " and " + labels[j] + ":")
            for part in parts:
                d = calculate_d(images[labels[i]][part].values.astype(float),
                                images[labels[j]][part].values.astype(float))
                c.append(d)
                print("\t" + part + ": " + str(d))
            cohen.append(c)

    return parts, cohen


def read_tsv(file: str):
    with open(file) as f:
        # Read the first line for the base image name
        base = f.readline().rstrip().split("\t")[0]
        # Read the second line for the column names
        second_line = f.readline().rstrip().split("\t")
    return base, pd.read_csv(file, sep="\t", skiprows=2, names=second_line)


def analyze(images: dict, labels: list, parts: list):
    print("============================== Shapiro-Wilk test ==============================")
    normal = shapiro_test(images, labels, parts)
    print("============================== One-way ANOVA test =============================")
    significance = anova_test(images, labels, parts)
    print("============================== Tukey HSD test =================================")
    tukey = tukey_test(images, labels, parts)
    print("============================== Cohen's d test =================================")
    cohen = cohen_d(images, labels, parts)
    return normal, significance, tukey, cohen


def parse_args(argv):
    file = list()
    statistical_test = ""

    # Get the arguments provided by the user
    opts, args = getopt.getopt(argv, "f:", ["file=", "shapiro", "anova", "tukey", "cohen", "full"])
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            file.append(arg)
        elif opt == "--shapiro":
            statistical_test = "shapiro"
        elif opt == "--anova":
            statistical_test = "anova"
        elif opt == "--tukey":
            statistical_test = "tukey"
        elif opt == "--cohen":
            statistical_test = "cohen"
        elif opt == "--full":
            statistical_test = "full"

    return file, statistical_test


def main(argv):
    images = {}
    file, statistical_test = parse_args(argv)

    # Read the TSV files
    for f in file:
        base, df = read_tsv(f)
        images[base] = df

    labels, parts = get_lists(images)

    if statistical_test == "shapiro":
        shapiro_test(images, labels, parts)
    elif statistical_test == "anova":
        anova_test(images, labels, parts)
    elif statistical_test == "tukey":
        tukey_test(images, labels, parts)
    elif statistical_test == "cohen":
        cohen_d(images, labels, parts)
    elif statistical_test == "full":
        analyze(images, labels, parts)


if __name__ == '__main__':
    main(sys.argv[1:])
