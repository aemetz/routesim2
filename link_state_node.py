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

            

            message = {'src': self.id, 'dst':neighbor, 'seq_num': self.seq_num, 'cost': latency, 'sender': self.id, 'last_msg': len(self.last_msg)}
            json_message = json.dumps(message)
            self.send_to_neighbors(json_message)

        self.seq_num += 1   
        

    # Fill in this function
    def process_incoming_routing_message(self, m):
        rec_msg = json.loads(m)

        # For regular messages
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
                # what should our condition be? CONSIDER USING GET_TIME
                # if rec_msg['last_msg'] < len(self.last_msg):
                #     message = {'costs': self.costs, 'all_nodes': self.all_nodes, 'other_neighbors': self.other_neighbors}
                #     json_message = json.dumps(message)
                #     self.send_to_neighbor(json_message)

                rec_msg['sender'] = self.id

                self.send_to_neighbors(json.dumps(rec_msg))

        # For catching-up-to-date messages
        # else:
        #     self.costs = rec_msg['costs']
        #     self.all_nodes = rec_msg['all_nodes']
        #     self.other_neighbors = rec_msg['other_neighbors']

        #     # Update shortest_dist and prev_node

        #     for node in self.all_nodes:
        #         if node != self.id and node not in self.prev_node and node not in self.shortest_dist:
        #             self.prev_node[node] = None
        #             self.shortest_dist[node] = float('inf')
         
            
    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # loop until we have visited all nodes
        # find an unvisited node whose distance from source is minimum

        # all nodes is good
        # print(self.all_nodes)

        print("-------------------------")
        print(self.id)
        print(self.shortest_dist)

        print("LAST_MSG DICT ---------- ")
        print(self.last_msg)

        while self.visited != self.all_nodes:
            # print("DIJKSTRA LOOP")
            # loop through shortest dist looking for minimum dist from source (unvisited)
            for w, val in self.shortest_dist.items():
                
                
                if val < float('inf') and w not in self.visited:
                    # add that node to visited
                    self.visited.add(w)
                    print("---------w = 1--------")
                    print(w == 1)

                    print("w's other neighbors ---------------")
                    print(self.other_neighbors[w])
                    print("costs of all connections -----------")
                    print(self.costs)
                    # each neighbor v of w and not in visited
                    for v in self.other_neighbors[w]:
                        if v not in self.visited:

                            if self.shortest_dist[w] + self.costs[frozenset([w, v])] < self.shortest_dist[v]:
                                self.shortest_dist[v] = self.shortest_dist[w] + self.costs[frozenset([w, v])]
                                self.prev_node[v] = w

        
        prev = -1
        curr = destination
        while curr != self.id:
            print("PREV WHILE LOOP")
            if curr in self.prev_node:
                prev = curr
                curr = self.prev_node[curr]
            else:
                prev = -1
                break

        return prev
