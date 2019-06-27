import networkx as nx
import matplotlib.pyplot as plt, mpld3
from operator import itemgetter
from matplotlib.patches import ConnectionPatch
import math

def find_route(circles):
    graph = {'%s'%i: [] for i in range(len(circles))}
    for i in range(len(circles) - 1):
        for j in range(i + 1, len(circles)):
            x1, y1, x2, y2 = circles[i][0], circles[i][1], circles[j][0], circles[j][1]
            r1, r2 = circles[i][2], circles[j][2]
            if have_edge(x1, y1, x2, y2, r1, r2):
                graph['%s'%i].append(j)

    path = find_path(graph, 0, len(circles) -1 )
    #print(graph)
    print(path)
    if path == []:
        print(-1)
    else:
        min_path = min(path, key=len)
        print(len(min_path) - 1)

        visualize(graph, min_path, circles)

def have_edge(x1, y1, x2, y2, r1, r2):
    dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return dist < r1 + r2 and dist > abs(r1-r2)

def find_path(graph, star_vertex, end_vertex, path=[]):
    path = path + [star_vertex]
    if(star_vertex == end_vertex):
        return [path]
    paths=[]
    for vertex in graph['%s'%star_vertex]:
        if vertex not in path:
            extended_path = find_path(graph, vertex, end_vertex, path)

            for p in extended_path:
                paths.append(p)
    return paths

def visualize(graph_data, path, circles):
    G = nx.DiGraph()
    for key in graph_data.keys():
        for connection in graph_data[key]:
            G.add_path([int(key), connection])

    fig, axs = plt.subplots()
    plt.figure(figsize=(8,6))

    node_colors = ['red' if n in path else 'blue' for n in G.nodes()]
    nx.draw_networkx(G, with_labels=True, node_color=node_colors)
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)

    i = 0
    for circle in circles:
        x, y, r = circle[0], circle[1], circle[2]
        c = plt.Circle((x, y), r, color='b', fill=False)
        axs.text(x, y, str(i))
        i += 1
        axs.add_patch(c)

    for i in range(len(path) - 1):
        c1, c2 = circles[path[i]], circles[path[i + 1]]
        conn = ConnectionPatch(xyA=(c1[0], c1[1]), xyB=(c2[0], c2[1]), coordsA='data', arrowstyle="-|>")
        axs.add_patch(conn)

    axs.autoscale()
    plt.show()



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

    