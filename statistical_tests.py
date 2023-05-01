import getopt
import sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def shapiro_test(data):
    print("False means that the null hypothesis is rejected, i.e. the data is not normal.")
    labels = list(data.keys())
    parts = list(data[labels[0]].columns)
    normal = list()
    for l in labels:
        n = list()
        for p in parts:
            x = data[l][p].values.astype(float)
            shapiro = stats.shapiro(x)
            if shapiro.pvalue < 0.05:
                n.append(False)
            else:
                n.append(True)
        normal.append(n)
        print(l + ": " + str(n))
    return labels, normal


def anova_test(data):
    print("False means that the null hypothesis is rejected, i.e. the means are not equal.")
    labels = list(data.keys())
    parts = list(data[labels[0]].columns)
    significance = list()
    for p in parts:
        x = list()
        s = True
        for l in labels:
            x.append(data[l][p].values.astype(float))
        anova = stats.f_oneway(*x)
        if anova.pvalue < 0.05:
            significance.append(False)
            s = False
        else:
            significance.append(True)
            s = True
        print(p + ": " + str(s))
    return parts, significance


def tukey_test(data):
    labels = list(data.keys())
    parts = list(data[labels[0]].columns)
    tukey = list()
    for p in parts:
        # for key, value in data.items():
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
        # read the first line for the base image name
        base = f.readline().rstrip().split("\t")[0]
        # read the second line for the column names
        second_line = f.readline().rstrip().split("\t")
    return base, pd.read_csv(file, sep="\t", skiprows=2, names=second_line)


def main(argv):
    images = {}
    file = list()
    statistical_test = ""
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