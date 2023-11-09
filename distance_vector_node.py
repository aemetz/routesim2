from simulator.node import Node
import json
import copy

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        # Distance vector for outbound links. Maps destination node to (cost, next_hop, path)
        self.dv = {}

        # Store the DV's of all the node's neighbors. Maps neighbor node id to their DV dictionary
        self.neighbor_dvs = {}

        # Store the latest msg from each (src, dst) pair to deal with out of order DV delivery. (Check seq_num)
        self.latest_msg = {}
        
        self.seq_num = 0

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency == -1:
            # if we delete a link, we have to update our DV and send the updated DV to neighbors
            if neighbor in self.dv:
                self.dv.pop(neighbor)
                

        else:
            self.dv[neighbor] = [latency, neighbor, [self.id, neighbor]]

            msg = {'src': self.id, 'dst': neighbor, 'seq_num': self.seq_num, 'dv': self.dv}
            json_message = json.dumps(msg)
            self.send_to_neighbors(json_message)
        

    # Fill in this function
    def process_incoming_routing_message(self, m):
        rec_msg = json.loads(m)

        src = int(rec_msg['src'])
        dst = int(rec_msg['dst'])
        seq_num = int(rec_msg['seq_num'])
        rec_dv = rec_msg['dv']

        key = frozenset((src, dst))
        
        # Check if we have received a msg before, if so compare seq_num to get most recent 
        if key in self.latest_msg:
            last_from_key = self.latest_msg[key]

            if seq_num > last_from_key['seq_num']:
                # rec_msg is the latest message
                self.latest_msg[key] = rec_msg

                # gather any "new" nodes (new to us) from the msg
                for node, val in rec_dv.items():
                    node = int(node)

                    # if any node from our neighbors is not in our dv, add it to our dv with initial value of inf
                    if node not in self.dv:
                        self.dv[node] = [float('inf'), src, [self.id, src, node]]


                for node in self.dv:
                    # 0 index represents cost 
                    # if the node is in our neighbor's dv, get its cost. else, use inf
                    dv_y = float('inf')
                    if node in rec_dv:
                        dv_y = rec_dv[node][0]
                        
                    if self.dv[src][0] + dv_y < self.dv[node][0]:
                        self.dv[node][0] = self.dv[src][0] + dv_y
                        # update next_hop?
                        self.dv[node][1] = src

                # Finished updating our DV, now send it to neighbors
                msg = {'src': self.id, 'dst': src, 'seq_num': self.seq_num, 'dv': self.dv}
                json_message = json.dumps(msg)
                self.send_to_neighbors(json_message)

                self.seq_num += 1

                # for each node y
                # update dv(y) = min of cost between x and it's neighbor (src) plus the neighbor's DV to y

                
                
        # If we haven't received a msg before, this is our latest msg
        else:
            self.latest_msg[key] = rec_msg


             # gather any "new" nodes (new to us) from the msg
            for node, val in rec_dv.items():
                node = int(node)

                # if any node from our neighbors is not in our dv, add it to our dv with initial value of inf
                if node not in self.dv:
                    self.dv[node] = [float('inf'), src, [self.id, src, node]]
                    

            for node in self.dv:
                # 0 index represents cost 
                # if the node is in our neighbor's dv, get its cost. else, use inf
                dv_y = float('inf')
                if node in rec_dv:
                    dv_y = rec_dv[node][0]
                
                # BLAHB:AHBAIBKEBUJKA---------------- ****************************************************************** HI
                # iterate through self.id neighbors when chcking bellman ford
                # instead of just checking src in  order to explore all minimum routes
                # from the source node
                # BLAHB:AHBAIBKEBUJKA *********************************************************************************
                
                if self.dv[src][0] + dv_y < self.dv[node][0]:
                    self.dv[node][0] = self.dv[src][0] + dv_y
                    self.dv[node][1] = src

            # Finished updating our DV, now send it to neighbors
            msg = {'src': self.id, 'dst': src, 'seq_num': self.seq_num, 'dv': self.dv}
            json_message = json.dumps(msg)
            self.send_to_neighbors(json_message)

            self.seq_num += 1

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        print("--------------------------------------------------")
        print(f'NODE ID: {self.id}')
        print(f"DV: {self.dv}")
        print(f'NEXT HOP: {self.dv[destination][1]}')
        return self.dv[destination][1]
