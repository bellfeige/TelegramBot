from DemnoksService.tele_bot.tele_bot import TeleBot
import os
import numpy as np
import matplotlib.pyplot as plt


class ChartController:
    def __init__(self):
        pass

    @staticmethod
    def init_chart(size_x=16, size_y=6, title="chart title", label_x="Date Time", label_y="Y value"):
        plt.gcf().set_size_inches(size_x, size_y)
        plt.title(title)
        plt.xlabel(label_x)
        plt.ylabel(label_y)

    @staticmethod
    def fill_chart(x_dt, y_dt):
        plt.plot(x_dt, y_dt)

    @staticmethod
    def chart_result(action='show', bbox_inches='tight', save_path='.', img_name='latest'):
        if action == 'show':
            plt.show()
        elif action == 'save':
            plt.savefig(f"{save_path}\\{img_name}", bbox_inches=bbox_inches)
        plt.clf()
