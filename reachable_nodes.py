# Load necessary packages
import sys
import networkx as nx
import os
import argparse
from tqdm import tqdm
import pandas as pd
import csv

# Function to compute temporally reachable nodes from a seed in a dairy network
def compute_temporally_reachable_nodes_from_seed(dairy_net, seed, epi_start_day, sim_end_day, deltaT):
    G = {}
    reachable_nodes = set()
    active_nodes = set()
    reachable_nodes.add(seed)
    active_nodes.add(seed)
    node_entry_time = {}
    node_entry_time[seed] = epi_start_day

    for t in range(epi_start_day, sim_end_day):
        if t > sim_end_day:
            break
        premises_to_remove = set()
        for premise in active_nodes:
            if node_entry_time[premise] + deltaT - t <= 0:
                #print(t, node_entry_time[premise])
                premises_to_remove.add(premise)
        
        active_nodes = active_nodes - premises_to_remove

        dairy_net_season = dairy_net.loc[
                (dairy_net.dayOfYear >= t) & (dairy_net.dayOfYear <= t),
                ['oPremId', 'dPremId', 'dayOfYear', 'volume']
        ]
        dairy_net_season = dairy_net_season.rename(columns={'oPremId':'origin'})
        dairy_net_season = dairy_net_season.rename(columns={'dPremId':'destination'})
        dairy_net_season = dairy_net_season.groupby(['origin', 'destination'])['volume'].sum().reset_index()
        filtered_dairy_net_season = dairy_net_season[dairy_net_season["origin"].isin(active_nodes)]

        if filtered_dairy_net_season.empty:
            continue
        #print(filtered_dairy_net_season.head(20))
        unique_destinations = set(filtered_dairy_net_season["destination"])
        new_destinations = unique_destinations - reachable_nodes
        for premise in new_destinations:
            node_entry_time[premise] = t
        reachable_nodes.update(new_destinations)
        active_nodes.update(new_destinations)
        #print(t, len(new_destinations), len(reachable_nodes))
    #print(f'Reachable premises from {seed}: {len(reachable_nodes)}')
    return len(reachable_nodes)



# main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Computing Temporally Nodes from Seed')
    parser.add_argument('--seed', type = int, help = 'Source need')
    parser.add_argument('--dn_path', type = str, help = 'Dairy networks path')
    parser.add_argument('--epi_start_day', type = int, help = 'Epidemic start date')
    parser.add_argument('--sim_end_day', type = int, help = 'Simulation end date')
    parser.add_argument('--output_path', type = str, help = 'Path to reachability output files')
    #parser.add_argument('--deltaT', type = int, help = 'threshold time')
    args = parser.parse_args()

    # Parameters
    seed = args.seed
    dn_path = args.dn_path
    epi_start_day = args.epi_start_day
    sim_end_day = args.sim_end_day
    output_dir_path = args.output_path
    #deltaT = args.deltaT
    #deltaT is the fixed infectious period
    deltaT_vals = [15, 30, 45, 60, 75, 90]
    num_dairy_networks = 1000

    file_template = "dairy_network_{}.network"
    print(f'Seed: {seed}')
    print(f'Dairy networks path: {dn_path}')
    print(f'Epidemic start date: {epi_start_day}')
    #print(f'Delta T: {deltaT}')
    reachable_node_map = {}
    fw = open(f"{output_dir_path}/reachable_map_seed_{seed}.csv", 'w')
    fw.write("deltaT,dairy_network,no_of_reachable_nodes\n")
    for i in tqdm(range(0, num_dairy_networks), desc="Processing", unit="iteration"):
        net_file_name = os.path.join(dn_path, file_template.format(i))
        #print(f'Processing file: {net_file_name}')
        dairy_net = pd.read_csv(net_file_name, sep = "\t")
        for deltaT in deltaT_vals:
            #print(f"deltaT: {deltaT}")
            no_reachable_nodes = compute_temporally_reachable_nodes_from_seed(dairy_net, seed, epi_start_day, sim_end_day, deltaT)
            reachable_node_map[(net_file_name, deltaT)] = no_reachable_nodes
            fw.write(f"{deltaT},{net_file_name},{no_reachable_nodes}\n")
        # Write the dictionary to a CSV file
        #with open(f"reachable_map_seed_{seed}.csv", mode="w", newline="") as file:
        #    writer = csv.writer(file)
        #    writer.writerow(["deltaT", "dairy_network", "no_of_reachable_nodes"])
        #    for key, value in reachable_node_map.items():
        #        writer.writerow([deltaT, key, value])
    fw.close()
