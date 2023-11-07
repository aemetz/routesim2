from simulator.node import Node
import json
# a

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        # Key: tuple, 
        self.all_msgs = {}
        self.seq_num = 0
        self.last_msg = {}
        
        # maps pair of nodes to cost of their edge
        self.costs = {}
        # maps node to distance from current node 
        self.shortest_dist = {}
        # maps node to previous node (where did we come from on the path)
        self.prev_node = {}
        # visited nodes
        self.visited = set([self.id])
        # all nodes
        self.all_nodes = set([self.id])

        self.neighbors = []

        self.other_neighbors = {}

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):

        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)

            #updating dict values

            key = frozenset((self.id, neighbor))
            self.costs.pop(key)
            
            self.shortest_dist[neighbor] = float('inf')

            self.prev_node[neighbor] = None

            # send message notifying other neighbors about deleted link, so they can update dictionary
            del_msg = {'src': self.id, 'dst': neighbor, 'seq_num': self.seq_num, 'cost': -1, 'sender': self.id}

            json_message = json.dumps(del_msg)
            self.send_to_neighbors(json_message)

            # remove the current node from its neighbor's other_neighbors dict, because link has been deleted
            if neighbor in self.other_neighbors:
                self.other_neighbors[neighbor].remove(self.id)
        
        else:

            #initialize Link state algorithim by recording neighbor costs
            print("ID, TIME ------------------------ X")
            print(self.id)
            print(self.get_time())
            key = frozenset((self.id, neighbor))
            self.costs[key] = latency
            
            self.shortest_dist[neighbor] = latency
            
            self.neighbors.append(neighbor)

            self.prev_node[neighbor] = self.id

            self.all_nodes.add(neighbor)

            # if self.costs.keys() > 0

            # update other_neighbors dict with the current node
            if neighbor in self.other_neighbors:
                if self.other_neighbors[neighbor]:
                    self.other_neighbors[neighbor].add(self.id)
            else:
                self.other_neighbors[neighbor] = set([self.id])

            

            message = {'src': self.id, 'dst':neighbor, 'seq_num': self.seq_num, 'cost': latency, 'sender': self.id, 'len_all_nodes': len(self.all_nodes), 'time': self.get_time()}
            json_message = json.dumps(message)
            self.send_to_neighbors(json_message)

        self.seq_num += 1   
        

    # Fill in this function
    def process_incoming_routing_message(self, m):
        rec_msg = json.loads(m)

        # For regular messages
        # change condition to something unique to message, not del_msg or up-to-date msg
        if 'src' in rec_msg:
            src = rec_msg['src']
            dst = rec_msg['dst']
            seq_num = rec_msg['seq_num']
            cost = rec_msg['cost']
            sender = rec_msg['sender']
            key = frozenset((src, dst))

            # add non-neighbors to 
            if src not in self.neighbors and src not in self.shortest_dist:
                self.shortest_dist[src] = float('inf')
                self.prev_node[src] = None
                

            self.all_nodes.add(src)

            if dst not in self.neighbors and dst not in self.shortest_dist:
                self.shortest_dist[dst] = float('inf')
                self.prev_node[dst] = None

          
            self.all_nodes.add(dst)


            #Updating Other Nodes' Neighbors

            if src in self.other_neighbors:
                self.other_neighbors[src].add(dst)
            else:
                self.other_neighbors[src] = set([dst])


            if dst in self.other_neighbors:
                self.other_neighbors[dst].add(src)
            else:
                self.other_neighbors[dst] = set([src])

            if key in self.all_msgs:
                if seq_num not in self.all_msgs[key]:
                    # msg not previously seen, so process it
                    self.all_msgs[key].append(seq_num)
                    
                    # record cost between nodes
                    self.costs[key] = cost

                    if seq_num > self.last_msg[key]:
                        self.last_msg[key] = seq_num
                        rec_msg['sender'] = self.id
                        self.send_to_neighbors(json.dumps(rec_msg))
                    else:
                        rec_msg['sender'] = self.id
                        self.send_to_neighbor(sender, json.dumps(rec_msg))
            else:
                # msg not previously seen, so process it
                self.all_msgs[key] = [seq_num]

                self.last_msg[key]  = seq_num

                # record cost between nodes
                self.costs[key] = cost

                # send information to new nodes to catch them up to date
                print("CHECK BEFORE IF STATEMENT LINE 162 --------------------- ")
                print(self.id)
                print(f"TIME: {rec_msg['time']}")
                print(f"TIME: {self.get_time()}")
                if rec_msg['len_all_nodes'] < len(self.all_nodes) and rec_msg['time'] > 0:
                    print(f"IF STATEMENT TRUE FOR NODE: {self.id}")
                    # convert sets to lists bc sets not json serializable
                    temp_all_nodes = list(self.all_nodes)
                    temp_other_neighbors = {}
                    print(f"ORIGINAL OTHER NEIGHBORS: {self.other_neighbors}")
                    for key in self.other_neighbors:
                        temp_other_neighbors[key] = list(self.other_neighbors[key])

                    print(f"TEMP OTHER NEIGHBORS: {temp_other_neighbors}")

                    temp_costs = {}
                    for key in self.costs:
                        temp_key = tuple(key)
                        key_str1 = str(temp_key[0])
                        comma = ","
                        key_str2 = str(temp_key[1])
                        temp_costs[key_str1 + comma + key_str2] = self.costs[key]

                    message = {'costs': temp_costs, 'all_nodes': temp_all_nodes, 'other_neighbors': temp_other_neighbors}
                    json_message = json.dumps(message)
                    self.send_to_neighbor(sender, json_message)

                rec_msg['sender'] = self.id

                self.send_to_neighbors(json.dumps(rec_msg))

        # For catching-up-to-date messages
        else:
            print("RECEIVED UP TO DATE MESSAGE----------------------------------------")
            print(self.id)

            
            self.all_nodes = set(rec_msg['all_nodes'])


            print("COMPARING OTHER_NEIGHBORS TO REC_MSG OTHER NEIGHBORS")
            print(f"other_neighbors: {self.other_neighbors}")
            print(f"rec_msg: {rec_msg['other_neighbors']}")
            

            for key in rec_msg['other_neighbors']:
                key = int(key)
                if key in self.other_neighbors:
                    self.other_neighbors[key] = self.other_neighbors[key].union(set(rec_msg['other_neighbors'][str(key)]))
                else:
                    self.other_neighbors[key] = set(rec_msg['other_neighbors'][str(key)])
                
                
            self.costs = {}

            for key in rec_msg['costs']:
                tuple_val = key.split(",")
                key1 = int(tuple_val[0])
                key2 = int(tuple_val[1])
                self.costs[frozenset((key1, key2))] = rec_msg['costs'][key]

            
            # print('NEW NODE MESSAGE RECEIVED ---------------------')
            print(f'COSTS OF THE GRAPH: {self.costs}')
            
            # Update shortest_dist and prev_node

            for node in self.all_nodes:
                if node != self.id and node not in self.prev_node and node not in self.shortest_dist:
                    self.prev_node[node] = None
                    self.shortest_dist[node] = float('inf')
         
            
    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # loop until we have visited all nodes
        # find an unvisited node whose distance from source is minimum

        # all nodes is good
        # print(self.all_nodes)

        print("-------------------------")
        print(self.id)
        print(self.shortest_dist)

        # print("LAST_MSG DICT ---------- ")
        # print(self.last_msg)
        print(f"VISITED: {self.visited}")
        print(f"OTHER NEIGHBORS: {self.other_neighbors}")

        self.visited = set([self.id])

        for node in self.shortest_dist:
            if node not in self.neighbors:
                self.shortest_dist[node] = float('inf')
            else:
                self.shortest_dist[node] = self.costs[frozenset((node, self.id))]

        while self.visited != self.all_nodes:
            # print("DIJKSTRA LOOP")
            # loop through shortest dist looking for minimum dist from source (unvisited)
            w = None
            val = float('inf')
            for node, dist in self.shortest_dist.items():
                print("SHORTEST DIST LOOP")
                if dist < val and node not in self.visited:
                    w = node
                    val = dist
                    
            # print(f"MINIMUM W: {w}")
            print("OUTERMOST LOOP")
                
            #MAIN ISSUE GUESS: fix it so that it iterates through all w's not in visited and its the minimum one, not just less then infinity
            # if w not in self.visited:
                # add that node to visited
            self.visited.add(w)
            print("---------w = 1--------")
            print(f"W: {w}")

            print("w's other neighbors ---------------")
            print(self.other_neighbors[w])
            print("costs of all connections -----------")
            print(self.costs)
            # each neighbor v of w and not in visited
            for v in self.other_neighbors[w]:

                print("LOOP")

                # fixes temp issue when deleted
                if v not in self.visited:

                    print("FIRST IF")

                    if self.shortest_dist[w] + self.costs[frozenset([w, v])] < self.shortest_dist[v]:
                        print("Second IF")
                        self.shortest_dist[v] = self.shortest_dist[w] + self.costs[frozenset([w, v])]
                        self.prev_node[v] = w


        prev = -1
        curr = destination
        print(f'START NODE: {self.id}')
        print(f'DESTINATION: {destination}')
        while curr != self.id:
            print("PREV WHILE LOOP")
            if curr in self.prev_node:
                prev = curr
                curr = self.prev_node[curr]
                # path.append(prev)
            else:
                print('ELSE OF PREV THING afireujf')
                prev = -1
                break
        print(f'PREV NODE DICT: {self.prev_node}')
        # print(f'auirgbn;efklj;na {path}')
        print(f'PREV: {prev}')
        return prev
        
