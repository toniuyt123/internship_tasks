
def goat(goats_count, min_courses, goats):
    goats.sort(reverse = True)
    capacity = goats[0]
    while True:
        used_space = 0
        current_trips = 0
        temp_goats = goats
        i = 0
        while i < len(goats):
            next_goat_index = biggest_goat(capacity - used_space, temp_goats)
            print('index:' + str(next_goat_index))
            if(next_goat_index > -1):
                if i == len(goats) - 1:
                    return capacity
                used_space += temp_goats[next_goat_index]

                print(temp_goats[next_goat_index])
                del temp_goats[next_goat_index]
            else:
                current_trips += 1
                used_space = 0
                i -= 1
                print('next_trip')
                if(current_trips == min_courses):
                    capacity += 1
                    print(capacity)
                    break
            i += 1

def biggest_goat(free_space, goats):
    for i in range(0, len(goats)):
        if(goats[i] <= free_space):
            return i
    return -1

if __name__ == '__main__':
    N, K = map(int, input().split())
    arr = list(map(int, input().split()))
    raft_capacity = goat(N, K, arr)
    print(raft_capacity)
