import pandas as pd


class clusterGenerator:
    def __init__(self, simulator, current_request_df):
        self.simulator = simulator
        self.request_df = current_request_df
        self.euclidean_radius = 0.5 # mile


    def euclidean_distance(self):

        # this method gives you shortest distance
        node1 = 65317547
        node2 = 4044911147

        distance = self.simulator.network.find_shortest_path_route(node1, node2)

        """
        pseudo-code
        
        initialize a graph
        add all requests as nodes
        
        for each request in request_df    
            draw a circle around the request coordinates
            get all requests within that circle
            
            for each request_in_circle in all_requests_in_circle:
                if no edge between request and request_in_circle:
                    compute distance from request's location to the location of each request_in_circle
                
                    if distance < walking_distance_threshold:
                        add edge between request and request_in_circle.        
        """
