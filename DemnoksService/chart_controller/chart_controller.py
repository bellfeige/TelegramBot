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
    def set_chart_data(x_dt, y_dt):
        plt.plot(x_dt, y_dt, '-o')
        for x, y in zip(x_dt, y_dt):
            label = "{:.6f}".format(y)

            plt.annotate(label,  # this is the text
                         (x, y),  # these are the coordinates to position the label
                         textcoords="offset points",  # how to position the text
                         xytext=(0, 5),  # distance from text to points (x,y)
                         ha='center')  # horizontal alignment can be left, right or center

    @staticmethod
    def set_chart_style():
        # plt.plot( )
        pass

    @staticmethod
    def show_chart_result(action='show', bbox_inches='tight', save_path='.', img_name='latest'):
        if action == 'show':
            plt.show()
        elif action == 'save':
            plt.savefig(f"{save_path}\\{img_name}", bbox_inches=bbox_inches)
        plt.clf()
