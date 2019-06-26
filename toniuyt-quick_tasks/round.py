import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import math

def find_route(circles):
    fig, ax = plt.subplots()
    for circle in circles:
        circle = plt.Circle((circle[0], circle[1]), circle[2])
        circle.set_facecolor('w')
        circle.set_edgecolor('c')
        ax.add_artist(circle)
    ax.margins(4, 4)

    graph = {'%s'%i: [] for i in range(len(circles))}
    for i in range(len(circles) - 1):
        for j in range(i + 1, len(circles)):
            x1, y1, x2, y2 = circles[i][0], circles[i][1], circles[j][0], circles[j][1]
            r1, r2 = circles[i][2], circles[j][2]
            if have_edge(x1, y1, x2, y2, r1, r2):
                graph['%s'%i].append(j)

    path = find_path(graph, 0, len(circles) -1 )
    print(len(path) - 1)
    plt.show()

def have_edge(x1, y1, x2, y2, r1, r2):
    return (x1 - x2)**2 + (y1 - y2)**2 <= (r1 + r2)**2 

def find_path(graph, star_vertex, end_vertex, path=None):
    if path is None:
        path = []
    path.append(star_vertex)
    if(star_vertex == end_vertex):
        return [path]
    paths=[]
    for vertex in graph['%s'%star_vertex]:
        if vertex not in path:
            extended_path = find_path(graph, vertex, end_vertex, path)

            if extended_path:
                return extended_path
    return None

if __name__ == '__main__':
    try:
        n = int(input())
        if n < 2 or n > 1000:
            raise ValueError('Invalid number of circles')
        circles = []
        for i in range(n):
            x,y,r = map(int, input().split())
            if x <= -10000 or x >= 10000 or y <= -10000 or y >= 10000 or r <= 0 or r >= 10000:
                raise ValueError('Invalid circle params')
            circles.append((x, y, r))

        find_route(circles)
    except ValueError as e:
        print(e)

    