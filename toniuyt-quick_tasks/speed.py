from collections import defaultdict
import networkx as nx

class RoadSpeed:
    g = {}

    def speed(self, n, roads):
        max_speed = max([r['speed'] for r in roads])
        min_speed = min([r['speed'] for r in roads])
        res_min = min_speed
        res_max = max_speed

        two_way = []
        speeds = []
        for r in roads:
            two_way.append(r)
            two_way.append({'road': (r['road'][1], r['road'][0]), 'speed': r['speed'] })
            if r['speed'] not in speeds: 
                speeds.append(r['speed'])
        speeds = sorted(speeds)

        for i in speeds:
            for j in speeds[speeds.index(i):]:
                self.g = dict.fromkeys(range(1, n+1))
                for k in self.g.keys():
                    self.g[k] = []
                for r in two_way:
                    if(r['speed'] >= i and r['speed'] <= j):
                        #print(r['road'][0])
                        self.g[r['road'][0]].append(r['road'][1])
                        #print(self.g[r['road'][0]])
                        #print('connections for')
                        #print(r['road'][0])
                        #print(g[r['road'][0]])
                has_isolated = False
                for k, v in self.g.items():
                    if v == []:
                        has_isolated = True
                        break
                #print(self.g)    
                #print(graph.nodes())
                print(i,j)
                if(not has_isolated and (j - i) < (res_max - res_min) and self.is_connected()):
                    res_max = j
                    res_min = i 
                    break
            
        print(res_max, res_min)

    def is_connected(self, vertices_encountered = None, start_vertex=None):
        """ determines if the graph is connected """
        if vertices_encountered is None:
            vertices_encountered = set()
        gdict = self.g      
        vertices = list(gdict.keys()) # "list" necessary in Python 3 
        if not start_vertex:
            # chosse a vertex from graph as a starting point
            start_vertex = vertices[0]
        vertices_encountered.add(start_vertex)
        if len(vertices_encountered) != len(vertices):
            for vertex in gdict[start_vertex]:
                if vertex not in vertices_encountered:
                    if self.is_connected(vertices_encountered, vertex):
                        return True
        else:
            return True
        return False

if __name__ == "__main__":
    try:
        N, M = map(int, input().split())
        if N < 2 or N > 1000 or M < 1 or M > 10000:
            raise ValueError("Invalid values")

        roads = []
        for i in range(M):
            F, T, S = map(int, input().split())
            if F < 1 or F > N or T < 1 or T > N or S < 1 or S > 30000:
                raise ValueError("Invlaid values")
            roads.append({'road': (F, T), 'speed': S})
        print('start')
        roadspeedcalc = RoadSpeed()
        roadspeedcalc.speed(N, roads)
    except ValueError as e:
        print(e)


'''
10 17
1 2 3 
1 2 5 
1 3 8 
2 4 16 
3 5 8 
3 6 19 
5 6 72 
7 8 9 
1 9 6 
4 7 5 
3 8 28 
4 2 15 
3 6 19 
7 8 16 
2 10 13 
1 10 1 
4 5 6

 
7 10
1 3 2
4 2 8
1 2 11
1 4 3
1 3 6
5 3 5
3 6 9
7 6 6
5 6 3
2 5 7
'''
