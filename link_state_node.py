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
        self.visited = [self.id]
        # unvisited nodes
        self.unvisited = []

        self.neighbors = []

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):

        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
        
        
        else:

            #initialize Link state algorithim by recording neighbor costs
            key = frozenset((self.id, neighbor.id))
            self.costs[key] = latency
            
            self.shortest_dist[neighbor.id] = latency
            
            self.neighbors.append(neighbor.id)

            self.prev_node[neighbor.id] = self.id

            self.unvisited.append(neighbor.id)


            message = {'src': self.id, 'dst':neighbor.id, 'seq_num': self.seq_num, 'cost': latency, 'sender': self.id}
            json_message = json.dumps(message)
            self.send_to_neighbors(json_message)

        self.seq_num += 1   
        

    # Fill in this function
    def process_incoming_routing_message(self, m):
        rec_msg = json.loads(m)
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
            self.unvisited.append(src)

        if dst not in self.neighbors and dst not in self.shortest_dist:
            self.shortest_dist[dst] = float('inf')
            self.prev_node[dst] = None
            self.unvisited.append(dst)

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

            rec_msg['sender'] = self.id

            self.send_to_neighbors(json.dumps(rec_msg))
            
        
        

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # loop until we have visited all nodes
        # find an unvisited node whose distance from source is minimum

        for node in self.unvisited:
            pass
        # add that node to visited
        # update the distance from the source of each neighbor of that unvisited node
        # that is not in visited


        return -1
