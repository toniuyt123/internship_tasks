
from collections import Counter

def goat(goats_count, min_courses, goats):
    goats.sort(reverse = True)
    capacity = goats[0]
    while True:
        free_space = capacity
        current_trips = 0
        sent_goats = []
        end = 0
        while True:
            next_goat = biggest_goat(free_space, goats, sent_goats)
            if(next_goat >= 0):
                free_space -= next_goat
                sent_goats.append(next_goat)
                sent_goats.sort(reverse=True)
                if sent_goats == goats:
                    return capacity
            else:
                current_trips += 1
                free_space = capacity
                if current_trips == min_courses:
                    capacity += 1
                    break
                

def biggest_goat(free_space, goats, sent_goats):
    c1 = Counter(goats)
    c2 = Counter(sent_goats)
    diff = c1-c2
    for i in range(0, len(goats)):
        if(goats[i] <= free_space and goats[i] in list(diff.elements())):
            return goats[i]
    return -1

if __name__ == '__main__':
    try:
        N, K = map(int, input().split())
        arr = list(map(int, input().split()))
        if N < 1 or N > 1000 or K < 1 or K > 1000 or max(arr) > 100000 or min(arr) < 1:
            raise ValueError('arguments out of bounds (1 ≤ N ≤ 1000, 1 ≤ K ≤ 1000, 1 ≤ Ai ≤ 100000)') 
        raft_capacity = goat(N, K, arr)
        print(raft_capacity)
    except ValueError as e:
        print(e)
