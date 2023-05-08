import getopt
import sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def get_lists(data):
    # Prepare the lists for the results
    # Labels are the base images
    labels = list(data.keys())
    # Parts are the different measurements (e.g. CPU, GPU, etc.)
    parts = list(data[labels[0]].columns)
    result = list()
    return labels, parts, result


def shapiro_test(data):
    print("False means that the null hypothesis is rejected, i.e. the data is not normal.")
    labels, parts, normal = get_lists(data)
    # Perform the Shapiro-Wilk test for normality for each part of each base image
    for l in labels:
        n = list()
        for p in parts:
            x = data[l][p].values.astype(float)
            shapiro = stats.shapiro(x)
            # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the data is not normal)
            if shapiro.pvalue < 0.05:
                n.append(False)
            else:
                n.append(True)
        normal.append(n)
        print(l + ": " + str(n))
    return labels, normal


def anova_test(data):
    print("False means that the null hypothesis is rejected, i.e. the means are not equal.")
    labels, parts, significance = get_lists(data)
    # Perform the one-way ANOVA test for each part between the base images
    for p in parts:
        x = list()
        s = True
        for l in labels:
            x.append(data[l][p].values.astype(float))
        anova = stats.f_oneway(*x)
        # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the means are not equal)
        if anova.pvalue < 0.05:
            significance.append(False)
            s = False
        else:
            significance.append(True)
            s = True
        print(p + ": " + str(s))
    return parts, significance


def tukey_test(data):
    labels, parts, tukey = get_lists(data)
    # Perform the Tukey HSD test for each part between the base images
    for p in parts:
        scores = list()
        for l in labels:
            scores.extend(data[l][p].values.astype(float))
        df = pd.DataFrame({'score': scores,
                           'group': np.repeat(labels, repeats=len(scores)/len(labels))})
        t = pairwise_tukeyhsd(endog=df['score'],
                              groups=df['group'],
                              alpha=0.05)
        tukey.append(t)
        print(p)
        print(t)
    return parts, tukey


def read_tsv(file):
    with open(file) as f:
        # Read the first line for the base image name
        base = f.readline().rstrip().split("\t")[0]
        # Read the second line for the column names
        second_line = f.readline().rstrip().split("\t")
    return base, pd.read_csv(file, sep="\t", skiprows=2, names=second_line)


def parse_args(argv):
    file = list()
    statistical_test = ""

    # Get the arguments provided by the user
    opts, args = getopt.getopt(argv, "f:", ["file=", "shapiro", "anova", "tukey"])
    for opt, arg in opts:
        if opt in ["-f", "--file"]:
            file.append(arg)
        if opt == "--shapiro":
            statistical_test = "shapiro"
        if opt == "--anova":
            statistical_test = "anova"
        if opt == "--tukey":
            statistical_test = "tukey"

    return file, statistical_test


def main(argv):
    images = {}
    file, statistical_test = parse_args(argv)

    # Read the TSV files
    for f in file:
        base, df = read_tsv(f)
        images[base] = df

    if statistical_test == "shapiro":
        shapiro_test(images)
    elif statistical_test == "anova":
        anova_test(images)
    elif statistical_test == "tukey":
        tukey_test(images)


if __name__ == '__main__':
    main(sys.argv[1:])