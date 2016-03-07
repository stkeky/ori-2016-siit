from __future__ import print_function


import random
import matplotlib.pyplot as plt


def linregress(x, y):
    assert len(x) == len(y)
    x_avg = sum(x) / float(len(x))
    y_avg = sum(y) / float(len(y))
    x_diff = [xi - x_avg for xi in x]
    y_diff = [yi - y_avg for yi in y]
    xy = [x_diff[i] * y_diff[i] for i in range(len(x))]  # kovarijansa
    xx = [x_diff[i] * x_diff[i] for i in range(len(x))]  # varijansa
    slope = sum(xy) / sum(xx)
    intercept = y_avg - slope * x_avg
    return slope, intercept


def predict(x, slope, intercept):
    return x * slope + intercept


def create_line(x, slope, intercept):
    y = [predict(xx, slope, intercept) for xx in x]
    return y

if __name__ == '__main__':
    x = range(50)
    random.seed(1337)
    y = [(i + random.randint(-5, 5)) for i in x]

    slope, intercept = linregress(x, y)

    line_y = create_line(x, slope, intercept)

    plt.plot(x, y, '.')
    plt.plot(x, line_y, 'b')
    plt.title('Slope: {0}, intercept: {1}'.format(slope, intercept))
    plt.show()

    print(y)
