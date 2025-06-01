from ilp_solver import ILP_Solver
from passenger_cluster_0430 import clusterGenerator

DEBUG = True

class ShuttleSim:
    def __init__(self, env, network, run_mode, request_df, end_time=36000):
        self.env = env
        self.network = network
        self.run_mode = run_mode #"benchmark for ilp"
        self.accumulation_time = 120
        self.end_time = end_time
        self.request_data = request_df
        self.current_request = []
        self.dispatch_trigger = env.event()
        self.matched_request_ids = set()
        self.clusters_over_time = {}

        if self.run_mode == "benchmark":
            self.ilp_solver = ILP_Solver(self.env, self.network, omega=900, max_delay=600)

        else:
            self.ilp_solver = None

    def reset(self):
        return 0

    def step(self):
        # request accumulate
        while True:
            print(f"[{self.env.now}] Tick")
            self.request_accumulate(self.env.now)

            clusterer = clusterGenerator(self, self.request_data)
            clusters = clusterer.extract_clusters()
            
            print(f"{len(clusters)}")

            # Store or use clusters (e.g., for dispatch, logging, analysis)
            self.current_clusters = clusters  # or handle them however needed

            yield self.env.timeout(self.accumulation_time)

            if self.env.now >= self.end_time:
                break
                
    def cluster_process(self):
        while self.env.now < self.end_time:
            self.current_request_df = self.request_accumulate(self.env.now)

            clusterer = clusterGenerator(self, self.current_request_df)
            G = clusterer.create_subgraph()
            clusters = clusterer.extract_clusters()

            print(f"[{self.env.now}] Found {len(clusters)} clusters.")
            self.clusters_over_time[self.env.now] = clusters

            yield self.env.timeout(self.accumulation_time)

    def request_accumulate(self, current_time):
        time_now = current_time
        time_next = time_now + self.accumulation_time

        request_df = self.request_data[
            (self.request_data["req_time"] >= time_now) & 
            (self.request_data["req_time"] < time_next)
        ]

        for _, request in request_df.iterrows():
            self.current_request.append(request.to_dict())

        if DEBUG:
            print(f"\t{self.env.now}: triggered request accumulate for ({time_now}, {time_next}) - current request {len(self.current_request)}")

        return request_df  # ✅ Return the DataFrame

    def trigger_dispatch(self):
        while True:
            print(f"{self.env.now}: Waiting for customer accumulation")
            yield self.dispatch_trigger
            print(f"[{self.env.now}] Tick | {len(self.current_request)} requests")

            if self.run_mode == "benchmark":
                matched = self.ilp_solver.solve(self.current_request)  # assume it returns matched requests
                matched_ids = {req['id'] for _, req in matched}  # or however your requests are structured
                self.matched_request_ids.update(matched_ids)
                print(f"\tMatched {len(matched_ids)} requests")

            if self.run_mode == "benchmark":
                self.ilp_solver.solve(self.current_request) # integer linear program

                # reinforcement learning

                print(f"\tbenchmark logic performed")
                # benchmark logic here

            # clear accumulated requests after dispatching
            self.current_request.clear()  # add conditional (clear served requests only) later
    
    def compute_match_rate(self):
        total_requests = len(self.request_data)
        matched_requests = len(self.matched_request_ids)
        return 100 * matched_requests / total_requests

    """
    Clustering Workflow
    
    - based on the aggregated requests
    - map to TAZ
    - perform clustering TAZ
    - fast clustering
        - k-means 
        - Dendogram
    - Ideally try to aim for <5 second for clustering of each TAZ
    """