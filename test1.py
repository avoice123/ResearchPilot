from scipy.io import loadmat

file_path = r"C:\Users\Administrator\Desktop\LK-手写数字 - 副本\MNIST_LK_readout10fold_Nv100_th200_results_v5_globalRMS.mat"

data = loadmat(file_path)

print(data.keys())
print(data['ACC_I'])
print(data['ACC_I'])
