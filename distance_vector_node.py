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

        # Store the neighbors of the current node
        self.neighbors = set([])

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
            if neighbor in self.neighbors:
                self.neighbors.remove(neighbor)
            if neighbor in self.neighbor_dvs:
                self.neighbor_dvs.pop(neighbor)
                

        else:
            self.neighbors.add(neighbor)

            
            
            # print("------------------ LINK HAS BEEN UPDATED -------------------")
            # print(self.id)
            # print(latency)
            # print(neighbor)

            
            self.dv[neighbor] = [latency, neighbor, [self.id, neighbor]]

            # print(self.dv[neighbor])

            msg = {'src': self.id, 'dst': neighbor, 'seq_num': self.seq_num, 'dv': self.dv}
            json_message = json.dumps(msg)
            self.send_to_neighbors(json_message)

        self.seq_num += 1
        

    # Fill in this function
    def process_incoming_routing_message(self, m):
        rec_msg = json.loads(m)

        src = int(rec_msg['src'])
        dst = int(rec_msg['dst'])
        seq_num = int(rec_msg['seq_num'])
        rec_dv = {}

        key = src

        for key1 in rec_msg['dv']:
            rec_dv[int(key1)] = rec_msg['dv'][key1]

        # self.neighbor_dvs[neighbor] = rec_dv
        
        # Check if we have received a msg before, if so compare seq_num to get most recent 
        if key in self.latest_msg:
            last_from_key = self.latest_msg[key]

            if seq_num > last_from_key['seq_num']:


                # if self.id == 1:
                #     print("UPDATING DV")
                #     print("====================================")
                    
                    
                # rec_msg is the latest message
                self.latest_msg[key] = rec_msg

                # gather any "new" nodes (new to us) from the msg
                for node, val in rec_dv.items():
                    node = int(node)

                    # if any node from our neighbors is not in our dv, add it to our dv with initial value of inf
                    if node not in self.dv:
                        self.dv[node] = [float('inf'), src, [self.id, src, node]]


                for node in self.dv:
                    
                    min_cost = float('inf')
                    min_neighbor = None

                    if node in self.neighbors or node == self.id:
                        continue

                    for neighbor in self.latest_msg:

                        d_v = self.latest_msg[neighbor]['dv']

                        # print('555555555555555555555555555555555555555555555555555555555555555555')
                        # print(f'self.id: {self.id}')
                        # print(f'neighbor: {neighbor}')
                        # print(f'self.dv: {self.dv}')
                        # print(f'd_v: {d_v}')
                        # print(f"self.dv[node]: {self.dv[node][0]}")
                        # print(f'node : {node}')
                        # print(self.latest_msg)


                        d_v_value = float('inf')
                    
                        if str(node) in d_v:
                            d_v_value = d_v[str(node)][0]
                       
                        if self.dv[neighbor][0] + d_v_value < min_cost:
                            min_neighbor = neighbor
                            min_cost = self.dv[neighbor][0] + d_v_value

                    self.dv[node][0] = min_cost
                    self.dv[node][1] = min_neighbor

                

                # Finished updating our DV, now send it to neighbors
                msg = {'src': self.id, 'dst': src, 'seq_num': self.seq_num, 'dv': self.dv}
                json_message = json.dumps(msg)
                self.send_to_neighbors(json_message)

                self.seq_num += 1

                # for each node y
                # update dv(y) = min of cost between x and it's neighbor (src) plus the neighbor's DV to y

                
                
        # If we haven't received a msg before, this is our latest msg
        else:
            # print(key)
            self.latest_msg[key] = rec_msg


             # gather any "new" nodes (new to us) from the msg
            for node, val in rec_dv.items():
                node = int(node)

                # if any node from our neighbors is not in our dv, add it to our dv with initial value of inf
                if node not in self.dv:
                    self.dv[node] = [float('inf'), src, [self.id, src, node]]
            # print("*************** REC_DV ******************")
            # print(self.id)
            # print(src)   
            # print(rec_dv)



            for node in self.dv:
                    
                min_cost = float('inf')
                min_neighbor = None

                if node in self.neighbors or node == self.id:
                    continue

                # print('1411111111111111111111111111111111111111111111')
                # print(f"self.latest_msg: {self.latest_msg}")


                for neighbor in self.latest_msg:

                    d_v = self.latest_msg[neighbor]['dv']
                    
                    # print('3iqt24hj9 ptwhgpiun 249t 204764278 =1 ==1 1= =1==1==')
                    # print(self.id)
                    # print(neighbor)
                    # print(self.dv)
                    # print(d_v)
                    # print(f"self.dv[node]: {self.dv[node][0]}")
                    # print(node)
                    


                    d_v_value = float('inf')
                    
                    if str(node) in d_v:
                        d_v_value = d_v[str(node)][0]

                    if self.dv[neighbor][0] + d_v_value < min_cost:
                        min_neighbor = neighbor
                        min_cost = self.dv[neighbor][0] + d_v_value

                self.dv[node][0] = min_cost
                self.dv[node][1] = min_neighbor

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
