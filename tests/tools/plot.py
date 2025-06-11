import matplotlib.pyplot as plt
import numpy as np


vs_1 = {'2x2': [1.022, 1.022, 1.022, 1.022, 1.025, 1.025, 1.026, 1.023, 1.024, 1.02], '5x5': [1.022, 1.022, 1.026, 1.024, 1.031, 1.022, 1.033, 1.024, 1.023, 1.025], '10x10': [2.04, 1.027, 1.028, 1.024, 1.034, 1.026, 2.045, 1.031, 1.029, 2.049]}
vs_3 = {'2x2': [1.025, 1.027, 1.031, 1.029, 1.03, 1.028, 1.03, 1.03, 1.026, 1.027], '5x5': [2.056, 2.052, 2.054, 2.058, 2.05, 3.094, 3.065, 2.04, 2.049, 3.057], '10x10': [8.084, 7.055, 8.082, 8.071, 8.074, 8.065, 8.076, 7.075, 8.105, 8.078]}
vs_10 = {'2x2': [1.031, 1.034, 1.034, 1.035, 1.042, 1.031, 1.038, 1.039, 1.036, 1.037], '5x5': [2.054, 3.067, 3.085, 3.086, 2.057, 2.077, 3.07, 2.055, 3.084, 2.057], '10x10': [8.215, 8.166, 9.229, 8.207, 8.161, 8.169, 8.246, 8.17, 8.178, 8.202]}
vs_100 = {'2x2': [3.118, 2.097, 2.092, 2.109, 1.064, 2.101, 2.089, 2.11, 2.109, 2.121], '5x5': [13.61, 12.579, 10.454, 10.477, 11.556, 11.502, 18.358, 11.783, 12.828, 9.509]}
monolit_1 = {'2x2': [0.015, 0.013, 0.012, 0.01, 0.009, 0.011, 0.009, 0.011, 0.013, 0.013], '5x5': [0.018, 0.009, 0.009, 0.011, 0.009, 0.01, 0.009, 0.011, 0.009, 0.01], '10x10': [0.014, 0.013, 0.014, 0.01, 0.01, 0.01, 0.01, 0.009, 0.012, 0.009]}
monolit_3 = {'2x2': [0.012, 0.013, 0.01, 0.011, 0.01, 0.012, 0.015, 0.011, 0.017, 0.011], '5x5': [0.009, 0.01, 0.012, 0.011, 0.012, 0.009, 0.012, 0.009, 0.013, 0.012], '10x10': [0.012, 0.01, 0.012, 0.009, 0.011, 0.011, 0.012, 0.011, 0.012, 0.01]}
monolit_10 = {'2x2': [0.014, 0.016, 0.017, 0.015, 0.016, 0.016, 0.015, 0.012, 0.014, 0.012], '5x5': [0.013, 0.013, 0.012, 0.015, 0.012, 0.012, 0.013, 0.012, 0.015, 0.011], '10x10': [0.014, 0.012, 0.013, 0.017, 0.012, 0.016, 0.015, 0.017, 0.014, 0.013]}
monolit_100 = {'2x2': [0.063, 0.051, 0.048, 0.057, 0.047, 0.058, 0.056, 0.061, 0.053, 0.056], '5x5': [0.057, 0.054, 0.053, 0.093, 0.074, 0.071, 0.073, 0.054, 0.056, 0.057], '10x10': [0.055, 0.053, 0.055, 0.063, 0.050, 0.062, 0.069, 0.092, 0.074, 0.083]}

# Create a boxplot
def plot_data(data, titel):
    keys = list(data.keys())
    values = list(data.values())
    plt.figure(figsize=(12, 8))
    box = plt.boxplot(values, labels=keys)
    for i in range(len(values)):
        y = values[i]
        x = np.random.normal(1 + i, 0.04, size=len(y))
        plt.plot(x, y, 'r.', alpha=0.2)
    plt.text(1, max(max(values)), f'Number of Values: {len(values[0])}', horizontalalignment='right',
             verticalalignment='top', transform=plt.gca().transAxes)
    plt.xlabel('Matrix Size')
    plt.title(titel)
    plt.ylabel('Seconds')
    plt.legend([box["boxes"][0]], ['RTT Values'], loc='upper right')
    plt.grid(True)
    plt.savefig(f'{titel}.png')


def plot_all(vs_1, vs_3, vs_10, vs_100, monolit_1, monolit_3, monolit_10, monolit_100):
    def plot_data(vs_data, monolit_data, titel, subplot_index):
        keys = list(vs_data.keys())
        vs_values = list(vs_data.values())
        monolit_values = list(monolit_data.values())

        plt.subplot(2, 2, subplot_index)
        box_vs = plt.boxplot(vs_values, positions=np.array(range(len(vs_values))) * 2.0 - 0.4, widths=0.6,
                             patch_artist=True, boxprops=dict(facecolor="C0"), medianprops=dict(color="blue"))
        box_monolit = plt.boxplot(monolit_values, positions=np.array(range(len(monolit_values))) * 2.0 + 0.4,
                                  widths=0.6,
                                  patch_artist=True, boxprops=dict(facecolor="C1"), medianprops=dict(color="orange"))

        plt.xticks(np.array(range(len(keys))) * 2.0, keys)
        plt.xlabel('Matrix Size')
        plt.title(titel)
        plt.ylabel('Seconds')
        plt.legend([box_vs["boxes"][0], box_monolit["boxes"][0]], ['VS', 'Monolit'], loc='upper right')
        plt.grid(True)


    plt.figure(figsize=(14, 10))

    plot_data(vs_1, monolit_1, '1. Worker Performance Test', 1)
    plot_data(vs_3, monolit_3, '3. Worker Performance Test', 2)
    plot_data(vs_10, monolit_10, '10. Worker Performance Test', 3)
    plot_data(vs_100, monolit_100, '100. Worker Performance Test', 4)

    plt.tight_layout()
    plt.savefig('comparison.png')
    plt.show()


if __name__ == '__main__':
    plot_all(vs_1, vs_3, vs_10, vs_100, monolit_1, monolit_3, monolit_10, monolit_100)
