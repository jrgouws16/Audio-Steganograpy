import numpy as np


noise = np.random.normal(0, 0.5, 100000)


belowSNR  = []

for i in range(5):
      belowSNR.append([0]*4)


print(belowSNR)
belowSNR[0][0] = 1
print(belowSNR)