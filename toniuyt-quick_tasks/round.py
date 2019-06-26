from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import GraphRenderer, StaticLayoutProvider, Oval, MultiLine
from bokeh.palettes import Spectral9

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
    #print(path)
    if path == []:
        print(-1)
    else:
        min_path = min(path, key=len)
        print(len(min_path) - 1)

        visualize(graph, min_path)

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

def visualize(graph_data, path):

    plot = figure(title='Graph Layout Demonstration', x_range=(-1.1,1.1), y_range=(-1.1,1.1),
              tools='', toolbar_location=None)
    graph = GraphRenderer()

    node_indices = list(map(int, graph_data.keys()))
    N = len(node_indices)
    ends = [item for sublist in graph_data.values() for item in sublist]
    starts = [int(item) for item in graph_data.keys() for k in range(len(graph_data[item]))]
    graph.node_renderer.data_source.add(node_indices, 'index')
    graph.node_renderer.data_source.add(['blue']*N, 'color')
    graph.node_renderer.glyph = Oval(height=0.1, width=0.2, fill_color='color')

    graph.edge_renderer.data_source.data = dict(
        start=starts,
        end=ends)

    circ = [i*2*math.pi/N for i in node_indices]
    x = [math.cos(i) for i in circ]
    y = [math.sin(i) for i in circ]

    graph_layout = dict(zip(node_indices, zip(x, y)))
    graph.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)
    
    plot.renderers.append(graph)

    output_file('graph.html')
    show(plot)



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

    