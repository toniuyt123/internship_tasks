import math
from copy import deepcopy

def cezarc(words):
  letters = []
  for word in words:
    for i in range(len(word)):
      if(word[i] not in letters):
        letters.append(word[i])
  
  graph = dict().fromkeys(letters)
  for k in graph.keys():
    graph[k] = []

  for i in range(len(words) - 1):
    min_len = min( len(words[i]), len(words[i + 1]) )
    for j in range(min_len):
      l1 = words[i][j]
      l2 = words[i + 1][j]
      if l1 != l2 and l2 not in graph[l1]:
        graph[l1].append(l2)
        break

  degree = {letter: 0 for letter in letters}
  for letter in letters:
    for k in graph:
      if letter in graph[k]:
        degree[letter] += 1

  sort = []
  visited = []

  while len(sort) < len(letters):
    found = False
    for l in degree:
      if degree[l] == 0 and l not in visited:
        found = True
        visited.append(l)
        for letter in graph[l]:
          degree[letter] -= 1
        
        sort.append(l)

    if not found:
      print('NO')
      return

  alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1) if chr(i) not in sort]
  print('YES')
  print(''.join(sort) + ''.join(alphabet))

  return 0

if __name__ == '__main__':
    try:
        n = int(input())
        if n <= 1 or n >= 100:
            raise ValueError('invalid data')

        words = []
        for i in range(n):
            words.append(input())

        cezarc(words)
    except ValueError as e:
        print(e)
