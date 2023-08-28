import getopt
import sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

import scikit_posthocs as sp
from cliffs_delta import cliffs_delta

import matplotlib.pyplot as plt

import matplotlib.ticker as ticker

from matplotlib.lines import Line2D
import seaborn as sns
import scripts.parse as parse

import os

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
            # print(list(x))
            try:
                x = images[label][part].values.astype(float)
                shapiro, p = stats.shapiro(list(x))
                z, p2 = stats.normaltest(list(x))
                r = False
                # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the data is not normal)
                if p < 0.05:
                    r = True
                data.append([part, r, p])
            except:
                print(f"Error in {part}")
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
    header = ["part", "reject", "p-value", "F-value"]
    data = list()
    # Perform the one-way ANOVA test for each part between the base images
    for part in parts:
        x = list()
        r = False
        for label in labels:
            x.append(images[label][part].values.astype(float))
        f, p = stats.f_oneway(*x)
        # print(p)
        # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the means are not equal)
        if p < 0.05:
            r = True
        data.append([part, r, p, f])
        # print("\t" + part + ": " + str(s))
        # print(p)
    print(pd.DataFrame(data, columns=header))
    # return parts, significance


def kruskal_test(images: dict, labels: list, parts: list):
    print(
        "============================== Kruskal-Wallis test ============================="
    )

    if len(labels) < 2:
        print("Not enough data to perform the test.")
        return

    print(
        "True means that the null hypothesis is rejected, i.e. the means are not equal.\n"
    )

    print(f"Kruskal-Wallis test between {', '.join(labels)}:")
    header = ["part", "reject", "p-value", "F-value"]
    data = list()
    # Perform the one-way ANOVA test for each part between the base images
    for part in parts:
        x = list()
        r = False
        for label in labels:
            x.append(images[label][part].values.astype(float))
        f, p = stats.kruskal(*x)
        # print(p)
        # If the p-value is less than 0.05, the null hypothesis is rejected (i.e. the means are not equal)
        if p < 0.05:
            r = True
        data.append([part, r, p, f])
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


def dunn_test(images: dict, labels: list, parts: list):
    print("============================== Dunn test =================================")

    if len(labels) < 2:
        print("Not enough data to perform the test.")
        return

    print("False means that the null hypothesis is rejected, i.e. the means are equal.")
    # Perform the Dunn test for each part between the base images
    for part in parts:
        scores = list()
        names = list()
        print(f"Dunn test for {part}:")
        try:
            for label in labels:
                scores.append(images[label][part].values.astype(float))
                names.append(label[: label.index("@")])
            p = sp.posthoc_dunn(scores)
            p = p.set_axis(names, axis="columns")
            p = p.set_axis(names, axis="index")
            p[p < 0.05] = True

            # p[p != True] = False
            print(p)
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


def cliff_d(images: dict, labels: list, parts: list):
    print(
        "============================== Cliff's delta test ================================="
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
        first_label = labels[i]
        if (
            labels[i]
            == "node@sha256b04c99456868ce5e52dfdd3307b3d2a212deeec792b29692e19fb8b9078ae125"
        ):
            first_label = "node:16@sha256b04c99456868ce5e52dfdd3307b3d2a212deeec792b29692e19fb8b9078ae125"
        elif (
            labels[i]
            == "node@sha25682bcf77a5de631c6b19f4449ccec82bfbb7d8f6c94d6ae3bdf760ed67e080cb1"
        ):
            first_label = "node:16-alpine@sha25682bcf77a5de631c6b19f4449ccec82bfbb7d8f6c94d6ae3bdf760ed67e080cb1"
        for j in range(i + 1, len(labels)):
            header = ["part", "d", "result"]
            data = list()

            second_label = labels[j]
            if (
                labels[j]
                == "node@sha256b04c99456868ce5e52dfdd3307b3d2a212deeec792b29692e19fb8b9078ae125"
            ):
                second_label = "node:16@sha256b04c99456868ce5e52dfdd3307b3d2a212deeec792b29692e19fb8b9078ae125"
            elif (
                labels[j]
                == "node@sha25682bcf77a5de631c6b19f4449ccec82bfbb7d8f6c94d6ae3bdf760ed67e080cb1"
            ):
                second_label = "node:16-alpine@sha25682bcf77a5de631c6b19f4449ccec82bfbb7d8f6c94d6ae3bdf760ed67e080cb1"

            print(
                "Cliff's delta effect size for "
                + first_label[: first_label.index("@")]
                + " and "
                + second_label[: second_label.index("@")]
                + ":"
            )
            for part in parts:
                d, res = cliffs_delta(
                    images[labels[i]][part].values.astype(float),
                    images[labels[j]][part].values.astype(float),
                )
                data.append([part, d, res])
                # print("\t" + part + ": " + str(d))
            # cohen.append(c)
            print(f"{pd.DataFrame(data, columns=header)}\n")


def statistics(images: dict, labels: list, parts: list):
    for label in labels:
        print(f"{label} (mean; standard deviation):")
        for part in parts:
            print(
                f"\t{part}: {np.mean(images[label][part].values.astype(float))}; "
                f"{np.std(images[label][part].values.astype(float))}"
            )


def plot(images: dict, labels: list, parts: list):
    # Boxplots
    for part in parts:
        label_names = list()
        compare = list()
        node_compare = list()
        node_label_names = list()
        for label in labels:
            if (
                label
                == "node@sha256b04c99456868ce5e52dfdd3307b3d2a212deeec792b29692e19fb8b9078ae125"
            ):
                node_label_names.insert(0, "node:16")
                node_compare.insert(0, images[label][part].values.astype(float))
            elif (
                label
                == "node@sha25682bcf77a5de631c6b19f4449ccec82bfbb7d8f6c94d6ae3bdf760ed67e080cb1"
            ):
                node_label_names.append("node:16-alpine")
                node_compare.append(images[label][part].values.astype(float))
            else:
                try:
                    label_names.append(label[: label.index("@")])
                except:
                    label_names.append(label)
                compare.append(images[label][part].values.astype(float))
        compare = compare + node_compare
        label_names = label_names + node_label_names
        plt.figure(figsize=(9, 7))
        # plt.boxplot(compare)
        # plt.violinplot(compare)
        sns.boxplot(data=compare)
        plt.xticks(range(0, len(labels)), label_names)
        plt.title(part)
        # try:
        #     plt.title(part.rsplit("_", 1)[1])
        # except:
        #     plt.title(part)
        # print(labels)
        # print(label_names)
        plt.show()

    # for label in labels:
    #     stats.probplot(
    #         images[label][part].values.astype(float), dist="norm", plot=plt
    #     )
    #     plt.title("Q-Q plot")
    #     plt.xlabel("Theoretical Quantiles")
    #     plt.ylabel("Sample Quantiles")
    #     plt.show()
    # df = pd.DataFrame()
    # for label in labels:  # in range(len(labels)):
    #     df_label = images[label].copy()
    #     df_label["Image"] = label[: label.index("@")]
    #     df = pd.concat([df, df_label], ignore_index=True)

    # One plot for all distributions
    # for part in parts:
    #     # for label in labels:
    #     # ax = sns.displot(images[label], x="CORE0_ENERGY (J)", kind="kde")
    #     # plt.title(label[: label.index("@")])

    #     # ax.set(xlim=(930, 1080))
    #     # ax.set(ylim=(0, 0.05))

    #     ax = sns.displot(data=df, x=part, hue="Image", kind="kde")
    #     plt.title(f"{part} distribution")
    #     plt.show()

    # Bar/Line Plot for all runs of each image
    # df = pd.DataFrame()
    # for label in labels:
    #     df_label = images[label].copy()
    #     df_label["Image"] = label[: label.index("@")]
    #     df = pd.concat([df, df_label], ignore_index=True)
    #     break

    # for part in parts:
    #     ax = sns.barplot(data=df, y=part, x="RUN", hue="Image")
    #     # ax = sns.lineplot(data=df, y=part, x="RUN", hue="Image")
    #     # ax.set(xlim=(0, 120))
    #     # ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
    #     # ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    #     plt.title(f"{part} over time")
    #     plt.show()


def plot_distribution(images: dict, labels: list, parts: list):
    df = pd.DataFrame()
    df_node = pd.DataFrame()
    for label in labels:  # in range(len(labels)):
        df_label = images[label].copy()
        if (
            label
            == "node@sha256b04c99456868ce5e52dfdd3307b3d2a212deeec792b29692e19fb8b9078ae125"
        ):
            df_label["Image"] = "node:16"
            df_node = pd.concat([df_label, df_node], ignore_index=True)
        elif (
            label
            == "node@sha25682bcf77a5de631c6b19f4449ccec82bfbb7d8f6c94d6ae3bdf760ed67e080cb1"
        ):
            df_label["Image"] = "node:16-alpine"
            df_node = pd.concat([df_node, df_label], ignore_index=True)
        else:
            try:
                df_label["Image"] = label[: label.index("@")]
            except:
                df_label["Image"] = label
            df = pd.concat([df, df_label], ignore_index=True)

    df = pd.concat([df, df_node], ignore_index=True)
    for part in parts:
        # for label in labels:
        # ax = sns.displot(images[label], x="CORE0_ENERGY (J)", kind="kde")
        # plt.title(label[: label.index("@")])

        # ax.set(xlim=(930, 1080))
        # ax.set(ylim=(0, 0.05))

        # plt.figure(figsize=(15, 7))
        # sns.set(rc={"figure.figsize": (15, 7)})
        g = sns.displot(
            data=df,
            x=part,
            hue="Image",
            kind="kde",
            height=7,
            aspect=1,
        )
        # if part == "CORE0_ENERGY (J)":
        #     g.set(xlabel="ENERGY (J)")
        # elif part == "ELAPSED_TIME (s)":
        #     g.set(xlabel="TIME (s)")
        # g = sns.displot(data=df, x=part, hue="Image", height=7, aspect=2)
        # plt.title(f"{part.rsplit('_', 1)[1]} distribution", y=0.95)
        # plt.legend(loc="upper right")
        plt.show()


def plot_correlation(images: dict, labels: list, parts: list):
    df = pd.DataFrame()
    for label in labels:
        # plt.figure(figsize=(10, 7))
        x = "TIME (s)"
        y = "ENERGY (J)"
        if len(df) == 0:
            df[x] = images[label][x]
            df[y] = images[label][y]
        else:
            df = pd.concat([df, images[label][[x, y]]], ignore_index=True)
        r = np.corrcoef(images[label][x], images[label][y])
        r = stats.pearsonr(images[label][x], images[label][y])
        print(f"{label}: {r}")

        # sns.relplot(
        #     data=images[label],
        #     x=x,
        #     y=y,
        # )
        # plt.title(label[: label.index("@")])
        # plt.show()
    # r = stats.pearsonr(df[x], df[y])
    # print(f"{r}")
    # print(df)


def plot_median(directory: str, images: dict, labels: list, parts: list):
    for part in parts:
        for i in range(len(labels)):
            label = labels[i]
            # if (
            #     label
            #     != "alpine@sha25625fad2a32ad1f6f510e528448ae1ec69a28ef81916a004d3629874104f8a7f70"
            # ):
            #     continue
            # compare.append(images[label][part].values.astype(float))
            sorted = images[label].sort_values(part)
            # print(sorted)
            middle = (len(sorted) - 1) // 2
            middle = 28
            index = sorted["RUN"].iloc[middle]
            # index = sorted["RUN"].iloc[6]
            # index = sorted["RUN"].iloc[24]
            # print(index)

            base, df = read_tsv(f"{directory}/{label}/run-{index}.tsv")
            df_samples = pd.DataFrame()
            df_samples = parse.get_greenserver_time(df_samples, df)
            df_samples = parse.get_greenserver_average_power(df_samples, df, [0])
            df_samples = parse.get_greenserver_cpu_usage(df_samples, df, range(0, 23))
            df_samples["CORE0_VOLT (V)"] = df["CORE0_VOLT (V)"].copy()
            df_samples["CORE0_PSTATE"] = df["CORE0_PSTATE"].copy()
            df_samples["CORE0_FREQ (MHZ)"] = df["CORE0_FREQ (MHZ)"].copy()
            # df_samples["GPU_POWER (W)"] = df["GPU_POWER (W)"].copy()
            # df_samples["GPU_USAGE"] = df["GPU_USAGE (%)"].copy()
            # x_value = "INTERVAL_ELAPSED_TIME (s)"
            x_value = "ELAPSED_TIME (s)"
            # y_value1 = f"CORE0_AVERAGE_POWER (W)"
            y_value1 = f"CORE0_ENERGY_SAMPLE (J/interval)"
            # y_value1 = f"GPU_POWER (W)"
            # y_value1 = f"CORE0_FREQ (MHZ)"
            # y_value1 = f"CORE0_ENERGY_SAMPLE_DIFF"
            # y_value1 = f"CORE0_PSTATE"
            y_value1 = f"CPU0_USAGE_DELTA"
            # y_value1 = f"GPU_USAGE"
            # y_value3 = f"CPU12_USAGE_DELTA"
            # y_value1 = "CORE0_VOLT (V)"
            df_smooth = pd.DataFrame()
            df_smooth = df_samples.iloc[::10, :].copy()

            # print(df_samples)

            # break

            df_smooth[f"CORE0_ENERGY_SAMPLE_DIFF"] = (
                df_smooth[f"CORE0_ENERGY_SAMPLE (J/interval)"]
                .diff()
                .fillna(0)
                .div(df_smooth["TIME_DELTA (s)"], axis=0)
                .fillna(0)
            )

            # r = stats.pearsonr(df_samples[y_value1], df_samples[y_value2])
            # print(f"{label[: label.index('@')]}: {r}")
            # ax = sns.relplot(
            #     data=df_samples,
            #     x=y_value1,
            #     y=y_value2,
            # )
            # ax.set(ylim=(5000, 6000))
            # plt.title(label[: label.index("@")])
            # plt.show()

            # print(df_samples)
            # print(df_samples["CORE0_AVERAGE_POWER (W)"].sum())
            ax = sns.lineplot(
                x=x_value,
                y=y_value1,
                # data=df_samples.iloc[::35, :],
                data=df_samples,
                # data=df_smooth
                # )
                # color="b",
            )
            # ax = sns.lineplot(
            #     x=x_value,
            #     y="CORE0_VOLT (V)",
            #     data=df_samples,
            #     # )
            #     # color="b",
            # )
            # ax2 = ax.twinx()
            # sns.lineplot(
            #     x=x_value,
            #     y=y_value2,
            #     data=df_samples,
            #     ax=ax2,
            #     color="g",
            # )
            # sns.lineplot(
            #     x=x_value,
            #     y=y_value3,
            #     data=df_samples,
            #     ax=ax2,
            #     color="y",
            # )
            # ax.legend(
            #     handles=[
            #         # Line2D([], [], marker="_", color="b", label="CORE0_AVERAGE_POWER (W)"),
            #         Line2D([], [], marker="_", color="b", label=y_value1),
            #         Line2D([], [], marker="_", color="g", label=y_value2),
            #         # Line2D([], [], marker="_", color="y", label=y_value3),
            #     ]
            # )
            # ax = sns.lineplot(
            #     x=x_value,
            #     y=y_value,
            #     data=df_samples,
            #     # color="b",
            # )
            # plt.title(
            #     f"Voltage over time for {label[: label.index('@')]} - run {index} ({int(sorted[part].iloc[middle])} J)"
            # )
            if (
                label
                == "node@sha256b04c99456868ce5e52dfdd3307b3d2a212deeec792b29692e19fb8b9078ae125"
            ):
                plt.title(
                    f"Energy over time for node:16 - run {index} ({int(sorted[part].iloc[middle])} J)"
                )
            elif (
                label
                == "node@sha25682bcf77a5de631c6b19f4449ccec82bfbb7d8f6c94d6ae3bdf760ed67e080cb1"
            ):
                plt.title(
                    f"Energy over time for node:16-alpine - run {index} ({int(sorted[part].iloc[middle])} J)"
                )
            else:
                # plt.title(
                #     f"Energy over time for {label[: label.index('@')]} - run {index} ({int(sorted[part].iloc[middle])} J)"
                # )
                try:
                    plt.title(
                        f"CPU usage over time for {label[: label.index('@')]} - run {index} ({int(sorted['CORE0_ENERGY (J)'].iloc[middle])} J)"
                    )
                except:
                    plt.title(
                        f"Energy over time for {label} - run {index} ({int(sorted['ENERGY (J)'].iloc[middle])} J)"
                    )
            # plt.title(
            #     f"Freq over time for {label[: label.index('@')]} - run {index} ({int(sorted[part].iloc[middle])} J)"
            # )
            # ax2.set(xlim=(-0.00000011, 0.00000051))
            # ax.set(xlim=(-10, 490), ylim=(-0.1, 1.7))
            # plt.title(
            #     f"P-state/usage over time for {label[: label.index('@')]} - run {index} ({int(sorted[part].iloc[middle])} J)"
            # )
            # break

            # ax.set(xlabel="TIME(s)", ylabel="ENERGY PER SAMPLE (J/100ms)")
            # for i in range(23):
            #     ax = sns.lineplot(
            #         x=x_value,
            #         y=f"CPU{i}_USAGE_DELTA",
            #         # data=df_samples.iloc[::35, :],
            #         data=df_samples,
            #         # data=df_smooth
            #         # )
            #         # color="b",
            #     )
            #     plt.show()
            plt.show()
            break
        # break


def plot_samples(directory: str):
    images = [
        image
        for image in os.listdir(directory)
        if os.path.isdir(f"{directory}/{image}")
    ]

    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 7))
    for image in images:
        df_run = pd.DataFrame()
        run = 0
        df_label = images[label].copy()
        files = parse.get_files(f"{directory}/{image}", "*.tsv")
        for file in files:
            df = pd.read_csv(
                file,
                sep="\t",
                usecols=["Delta", "CORE0_ENERGY (J)", "ELAPSED_TIME (s)"],
            )
            df["CORE0_POWER (W)"] = (
                df["CORE0_ENERGY (J)"]
                .diff()
                .fillna(0)
                .div(df["Delta"], axis=0)
                .fillna(0)
                .multiply(1000)
            )
            df["Run"] = run
            df["Image"] = image
            run += 1

            if df_run.empty:
                df_run = df
            else:
                df_run = pd.concat([df_run, df], ignore_index=True)
        try:
            # print(df_run)
            x_value = "ELAPSED_TIME (s)"
            y_value = "CORE0_POWER (W)"

            sns.lineplot(x=x_value, y=y_value, data=df_run, hue="Image")
            plt.title("Power usage over time")
            plt.show()
        except:
            print("Incorrect values for x and y")


def analyze(images: dict, images_samples: dict, labels: list, parts: list):
    normal = shapiro_test(images, labels, parts)
    significance = anova_test(images, labels, parts)
    tukey = tukey_test(images, labels, parts)
    cohen = cohen_d(images, labels, parts)
    # plot(images, labels, parts)
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
    # df = pd.read_csv(
    #     file,
    #     sep="\t",
    #     skiprows=1,
    #     header=None,
    #     usecols=[0],
    #     names=["Time"],
    # )
    # df["Time"] = df["Time"].div(1000)
    # return base, df


def parse_args(argv):
    directory = ""
    files = list()
    parts = list()
    statistical_test = list()
    x_value = ""
    y_value = ""
    file_type = ""

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
            "kruskal",
            "tukey",
            "dunn",
            "cohen",
            "cliff",
            "full",
            "statistics",
            "plot",
            "plot-median",
            "plot-distribution",
            "plot-correlation",
            "plot-samples",
            "samples",
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
        elif opt == "--kruskal":
            statistical_test.append("kruskal")
        elif opt == "--tukey":
            statistical_test.append("tukey")
        elif opt == "--dunn":
            statistical_test.append("dunn")
        elif opt == "--cohen":
            statistical_test.append("cohen")
        elif opt == "--cliff":
            statistical_test.append("cliff")
        elif opt == "--full":
            statistical_test.append("full")
        elif opt == "--statistics":
            statistical_test.append("statistics")
        elif opt == "--plot":
            statistical_test.append("plot")
        elif opt == "--plot-median":
            statistical_test.append("plot-median")
        elif opt == "--plot-distribution":
            statistical_test.append("plot-distribution")
        elif opt == "--plot-correlation":
            statistical_test.append("plot-correlation")
        elif opt == "--plot-samples":
            statistical_test.append("plot-samples")
        elif opt == "-x":
            x_value = arg
        elif opt == "-y":
            y_value = arg
        elif opt == "--samples":
            file_type = "samples"

    return directory, files, parts, statistical_test, x_value, y_value, file_type


def main(argv):
    images = {}
    images_samples = {}
    directory, files, parts, statistical_test, x_value, y_value, file_type = parse_args(
        argv
    )

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

    # TODO: Interpolation of data samples

    # if file_type == "samples":
    #     images["ubuntulatest"] = images["ubuntulatest"].groupby("Run")["Watts"].mean().reset_index()
    labels, all_parts = get_lists(images)

    for p in parts:
        if p not in all_parts:
            print(
                f"Part {p} not found in the data; choose one from: {', '.join(all_parts)}"
            )
            return

    if len(parts) == 0:
        parts = all_parts

    labels = list(images.keys())

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
    if "kruskal" in statistical_test:
        kruskal_test(images, labels, parts)
    if "tukey" in statistical_test:
        tukey_test(images, labels, parts)
    if "dunn" in statistical_test:
        dunn_test(images, labels, parts)
    if "cohen" in statistical_test:
        cohen_d(images, labels, parts)
    if "cliff" in statistical_test:
        cliff_d(images, labels, parts)
    if "statistics" in statistical_test:
        statistics(images, labels, parts)
    if "plot" in statistical_test:
        plot(images, labels, parts)
    if "plot-median" in statistical_test:
        plot_median(directory, images, labels, parts)
    if "plot-distribution" in statistical_test:
        plot_distribution(images, labels, parts)
    if "plot-correlation" in statistical_test:
        plot_correlation(images, labels, parts)
    if "plot-samples" in statistical_test:
        plot_samples(directory)


if __name__ == "__main__":
    main(sys.argv[1:])
