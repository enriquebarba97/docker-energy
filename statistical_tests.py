import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def shapiro_test(*groups):
    normal = list()
    for x in groups:
        shapiro = stats.shapiro(x)
        if shapiro.pvalue < 0.05:
            normal.append(False)
        else:
            normal.append(True)
    return normal


def anova_test(*x):
    anova = stats.f_oneway(*x)
    if anova.pvalue < 0.05:
        return False
    return True


rng1 = np.random.default_rng()
rng2 = np.random.default_rng()
rng3 = np.random.default_rng()
x = stats.norm.rvs(loc=1, scale=6, size=100, random_state=rng1)
# y = stats.norm.rvs(loc=1, scale=6, size=100, random_state=rng1)
# z = stats.norm.rvs(loc=1, scale=6, size=100, random_state=rng1)
y = stats.norm.rvs(loc=4, scale=1, size=100, random_state=rng2)
z = stats.norm.rvs(loc=8, scale=9, size=100, random_state=rng3)

print(shapiro_test(x, y, z))

if False in shapiro_test(x, y, z):
    print("Not normal")
else:
    if anova_test(x, y, z):
        print("No significant differences")
    else:
        scores = np.append(x, [y, z])
        df = pd.DataFrame({'score': scores,
                           'group': np.repeat(['x', 'y', 'z'], repeats=100)})

        tukey = pairwise_tukeyhsd(endog=df['score'],
                                  groups=df['group'],
                                  alpha=0.05)
        print(tukey)

