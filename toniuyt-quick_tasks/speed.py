def speed(n, roads):
    paths = []
    two_way = []
    for r in roads:
        two_way.append(r)
        two_way.append({'road': (r['road'][1], r['road'][0]), 'speed': r['speed'] })
    #print(two_way)
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            res = find_path(i, j, two_way, [])
            #print('result' + str(res))
            paths.append(list(set(res)))

    max_speed = max([min(s) for s in paths])
    min_speed = min([max(list(filter(lambda x: x <= max_speed, s))) for s in paths])
    #print(list(filter(lambda x: x < max_speed, paths[1])))
    print(paths)
    print(max_speed)
    print(min_speed)
    return 0

def find_path(start, end, roads, trail, min_speed = 0):
    speeds = []
    #print('start:' + str(start))
    #print('end:' + str(end))
    for r in roads:
        '''if r['road'] == (start, end):
            speeds.append(r['speed'])
        elif r['road'][0] == start:
            found = find_path(r['road'][1], end, roads)
            if found != 0:
                speeds.append(r['speed'])
                speeds.append(found)
            print('found' + str(found))'''
        if r['road'] == (start, end):
            speeds.append(r['speed'])
        elif r['road'][0] == start and r['road'][1] not in trail:
            trail.append(r['road'][1])
            found = find_path(r['road'][1], end, roads, trail)
            print(found)
            if found != 0:
                #speeds.append(r['speed'])
                for f in found:
                    speeds.append(f)
                #speeds.append(found)
    #print("speeds for" + str(start) + str(end))
    #print(speeds)
    if speeds:
        return speeds
    return 0


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

        speeds = speed(N, roads)
    except ValueError as e:
        print(e)