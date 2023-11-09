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

            if key not in self.all_msgs:
                self.all_msgs[key] = [self.seq_num]
            else:
                self.all_msgs[key].append(self.seq_num)

            self.prev_node[neighbor] = None
            # send message notifying other neighbors about deleted link, so they can update dictionary
            del_msg = {'src': self.id, 'dst': neighbor, 'seq_num': self.seq_num, 'cost': -1, 'sender': self.id, 'del': True}
            json_message = json.dumps(del_msg)
            self.send_to_neighbors(json_message)
            # remove the current node from its neighbor's other_neighbors dict, because link has been deleted
            if neighbor in self.other_neighbors:
                self.other_neighbors[neighbor].remove(self.id)
        else:
            #initialize Link state algorithim by recording neighbor costs
            key = frozenset((self.id, neighbor))
          
            self.costs[key] = latency
            self.shortest_dist[neighbor] = latency
            
            self.neighbors.append(neighbor)

            self.prev_node[neighbor] = self.id

            self.all_nodes.add(neighbor)
            if key not in self.all_msgs:
                self.all_msgs[key] = [self.seq_num]
            else:
                self.all_msgs[key].append(self.seq_num)

            # update other_neighbors dict with the current node
            if neighbor in self.other_neighbors:
                if self.other_neighbors[neighbor]:
                    self.other_neighbors[neighbor].add(self.id)
            else:
                self.other_neighbors[neighbor] = set([self.id])

            temp_last_msg = {}

            alt_message = {'src': self.id, 'dst':neighbor, 'seq_num': self.seq_num, 'cost': latency}
            self.last_msg[key] = alt_message
            
            for key in self.last_msg:
                temp_key = tuple(key)
                key_str1 = str(temp_key[0])
                comma = ","
                key_str2 = str(temp_key[1])
                temp_last_msg[key_str1 + comma + key_str2] = self.last_msg[key]
            
            message = {'src': self.id, 'dst':neighbor, 'seq_num': self.seq_num, 'cost': latency, 'sender': self.id, 'last_msg': temp_last_msg, 'time': self.get_time()}

            json_message = json.dumps(message)
            self.send_to_neighbors(json_message)

        self.seq_num += 1   
        
    # Fill in this function
    def process_incoming_routing_message(self, m):
        rec_msg = json.loads(m)

        # For node deleted messages
        if 'del' in rec_msg:
            src = rec_msg['src']
            dst = rec_msg['dst']
            seq_num = rec_msg['seq_num']
            cost = rec_msg['cost']
            sender = rec_msg['sender']
            key = frozenset((src, dst))

            if key in self.all_msgs:
                if seq_num not in self.all_msgs[key]:
                    # msg not previously seen, so process it
                    self.all_msgs[key].append(seq_num)
                    
                    if key in self.costs:
                        del self.costs[key]
                        
                    if src in self.other_neighbors:
                        if dst in self.other_neighbors[src]:
                            self.other_neighbors[src].remove(dst)

                    if dst in self.other_neighbors:
                        if src in self.other_neighbors[dst]:
                            self.other_neighbors[dst].remove(src)

                    if seq_num > self.last_msg[key]['seq_num']:
                        message = {'src': src, 'dst':dst, 'seq_num': seq_num, 'cost': cost}
                        self.last_msg[key] = message
                        rec_msg['sender'] = self.id
                        self.send_to_neighbors(json.dumps(rec_msg))
                    elif seq_num < self.last_msg[key]['seq_num']:
                        rec_msg['sender'] = self.id
                        self.send_to_neighbor(sender, json.dumps(rec_msg))
            else:
                self.all_msgs[key] = [seq_num]
                message = {'src': src, 'dst':dst, 'seq_num': seq_num, 'cost': cost}
                self.last_msg[key]  = message
                    
                del self.costs[key]
                self.other_neighbors[src].remove(dst)
                self.other_neighbors[dst].remove(src)

                rec_msg['sender'] = self.id
                self.send_to_neighbors(json.dumps(rec_msg))
                
        # For regular messages
        # change condition to something unique to message, not del_msg or up-to-date msg
        elif 'src' in rec_msg:
            src = rec_msg['src']
            dst = rec_msg['dst']
            seq_num = rec_msg['seq_num']
            cost = rec_msg['cost']
            sender = rec_msg['sender']
            last_msg = {}

            key = frozenset((src, dst))
           
            for key_for in rec_msg['last_msg']:
                tuple_val = key_for.split(",")
                key1 = int(tuple_val[0])
              
                key2 = int(tuple_val[1])
             
                last_msg[frozenset((key1, key2))] = rec_msg['last_msg'][key_for]

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

                    if seq_num > self.last_msg[key]['seq_num']:
                        message = {'src': src, 'dst':dst, 'seq_num': seq_num, 'cost': cost}
                        self.last_msg[key] = message
                        rec_msg['sender'] = self.id
                        self.send_to_neighbors(json.dumps(rec_msg))
                    elif seq_num < self.last_msg[key]['seq_num']:
                        rec_msg['sender'] = self.id
                        self.send_to_neighbor(sender, json.dumps(rec_msg))
                        
                else:

                    check_last_msg = False
                
                    if (len(self.last_msg) > len(last_msg)) and rec_msg['time'] > 0:

                        check_last_msg = True

                    if check_last_msg and rec_msg['time'] > 0:
                        # convert sets to lists bc sets not json serializable
                        temp_all_nodes = list(self.all_nodes)
                        temp_other_neighbors = {}
                        for key in self.other_neighbors:
                            temp_other_neighbors[key] = list(self.other_neighbors[key])


                        temp_last_msg = {}
                        for key in self.last_msg:
                            temp_key = tuple(key)
                            key_str1 = str(temp_key[0])
                            comma = ","
                            key_str2 = str(temp_key[1])
                            temp_last_msg[key_str1 + comma + key_str2] = self.last_msg[key]

                        message = {'last_msg': temp_last_msg, 'all_nodes': temp_all_nodes, 'other_neighbors': temp_other_neighbors}
                        json_message = json.dumps(message)
                        self.send_to_neighbor(sender, json_message)

            else:
                # msg not previously seen, so process it
                self.all_msgs[key] = [seq_num]
                message = {'src': src, 'dst':dst, 'seq_num': seq_num, 'cost': cost}
                
                self.last_msg[key]  = message

                # record cost between nodes
                
                self.costs[key] = cost

                # send information to new nodes to catch them up to date

                check_last_msg = False
                
                if (len(self.last_msg) > len(last_msg)) and rec_msg['time'] > 0:

                    check_last_msg = True
        
                if check_last_msg and rec_msg['time'] > 0:
                    # convert sets to lists bc sets not json serializable
                    temp_all_nodes = list(self.all_nodes)
                    temp_other_neighbors = {}
                    for key in self.other_neighbors:
                        temp_other_neighbors[key] = list(self.other_neighbors[key])

                    temp_last_msg = {}
                    for key in self.last_msg:
                        temp_key = tuple(key)
                        key_str1 = str(temp_key[0])
                        comma = ","
                        key_str2 = str(temp_key[1])
                        temp_last_msg[key_str1 + comma + key_str2] = self.last_msg[key]

                    message = {'last_msg': temp_last_msg, 'all_nodes': temp_all_nodes, 'other_neighbors': temp_other_neighbors}
                    json_message = json.dumps(message)
                    self.send_to_neighbor(sender, json_message)

                rec_msg['sender'] = self.id

                self.send_to_neighbors(json.dumps(rec_msg))

        # For catching-up-to-date messages
        else:
          
            #CHANGED
            # self.all_nodes = set(rec_msg['all_nodes'])

            for node in rec_msg['all_nodes']:
                if node not in self.all_nodes:
                    self.all_nodes.add(node)

            for key in rec_msg['other_neighbors']:
                key = int(key)
                if key in self.other_neighbors:
                    self.other_neighbors[key] = self.other_neighbors[key].union(set(rec_msg['other_neighbors'][str(key)]))
                else:
                    self.other_neighbors[key] = set(rec_msg['other_neighbors'][str(key)])
                
                
            temp_last_msg = {}

            for key in rec_msg['last_msg']:
                tuple_val = key.split(",")
                key1 = int(tuple_val[0])
                key2 = int(tuple_val[1])
             
                temp_last_msg[frozenset((key1, key2))] = rec_msg['last_msg'][key]

   
            # remove the current node from its neighbor's other_neighbors dict, because link has been deleted

            for key in temp_last_msg:

                if key in self.all_msgs:
                    self.all_msgs[key].append(temp_last_msg[key]['seq_num'])
                else:
                    self.all_msgs[key] = [temp_last_msg[key]['seq_num']]

                if key in self.last_msg:
                    if self.last_msg[key]['seq_num'] < temp_last_msg[key]['seq_num']:
                        self.last_msg[key] =  temp_last_msg[key]
                        if self.last_msg[key]['cost'] != -1:
                            
                            self.costs[key] = self.last_msg[key]['cost']
                        else:

                            src = self.last_msg[key]['src']
                            dst = self.last_msg[key]['dst']

                            
                            self.costs.pop(key)
                            
                            if src in self.other_neighbors:
                                self.other_neighbors[src].remove(dst)
                            if dst in self.other_neighbors:
                                self.other_neighbors[dst].remove(src)
                else:
                    self.last_msg[key] = temp_last_msg[key]
                    if self.last_msg[key]['cost'] != -1:
                        self.costs[key] = self.last_msg[key]['cost']
                        
            # Update shortest_dist and prev_node
            for node in self.all_nodes:
                if node != self.id and node not in self.prev_node and node not in self.shortest_dist:
                    self.prev_node[node] = None
                    self.shortest_dist[node] = float('inf')
         
            
    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # loop until we have visited all nodes
        # find an unvisited node whose distance from source is minimum

        for key in self.last_msg:
            self.costs[key] = self.last_msg[key]['cost']
            
        self.visited = set([self.id])

        for node in self.shortest_dist:
            if node not in self.neighbors:
                self.shortest_dist[node] = float('inf')
            else:
                self.shortest_dist[node] = self.costs[frozenset((node, self.id))]

        while self.visited != self.all_nodes:
            w = None
            val = float('inf')

            for node, dist in self.shortest_dist.items():
                if dist < val and node not in self.visited:
                    w = node
                    val = dist
                    
            self.visited.add(w)

            for v in self.other_neighbors[w]:

                # fixes temp issue when deleted
                if v not in self.visited:

                    if self.shortest_dist[w] + self.costs[frozenset([w, v])] < self.shortest_dist[v]:
                        self.shortest_dist[v] = self.shortest_dist[w] + self.costs[frozenset([w, v])]
                        self.prev_node[v] = w


        prev = -1
        curr = destination
    
        while curr != self.id:
            if curr in self.prev_node:
                prev = curr
                curr = self.prev_node[curr]
            else:
                prev = -1
                break
     
        return prev
        
