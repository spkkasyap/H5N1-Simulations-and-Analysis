import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import argparse

def plot_reachability_vs_deltaT(seed: int):
    """Plot number of temporally reachable nodes vs Δt for each dairy network, 
       with no markers and a reference line at y=979."""
    # 1) Read in your data
    filename = f'outputs/reachable_map_seed_{seed}.csv'
    df = pd.read_csv(filename)

    # 2) Journal‑ready style
    plt.rc('font', family='serif', size=12)
    plt.rc('axes', titlesize=14, labelsize=14)
    plt.rc('xtick', labelsize=12)
    plt.rc('ytick', labelsize=12)

    # 3) Create figure
    fig, ax = plt.subplots(figsize=(6, 4))

    n_networks = df['dairy_network'].nunique()
    print(f'No. of networks: {n_networks}')
    # 4) Plot each dairy network as a plain black line
    count = 0
    for network, group in df.groupby('dairy_network'):
        count+=1
        grp = group.sort_values('deltaT')
        ax.plot(
            grp['deltaT'],
            grp['no_of_reachable_nodes'],
            color='k',
            linestyle='-',
            linewidth=1,
            alpha=0.05  # adjust transparency as desired
        )
    print(f'Number of dairy networks: {count}')
    # 5) Add horizontal reference line at y=979
    ax.axhline(
        y=979,
        color='red',
        linestyle='--',
        linewidth=1,
        alpha=0.5
    )

    xticks = sorted(df['deltaT'].unique())
    ax.set_xticks(xticks)
    ax.set_xlabel(r'Fixed Infectious Period ($\Delta t$)')

    # 6) Legend using proxy artists
    proxy_line = mlines.Line2D([], [], color='k', linestyle='-')
    ref_line   = mlines.Line2D([], [], color='red', linestyle='--')
    ax.legend(
        [proxy_line, ref_line],
        ['Dairy Network', 'Confirmed cases on 28-Feb-2025'],
        frameon=False,
        loc='upper right'
    )

    # 7) Labels and title
    ax.set_xlabel(r'Fixed Infectious Period ($\Delta t$)')
    ax.set_ylabel('# Temporally Reachable Nodes')
    ax.set_title(f'Seed = {seed}')

    fig.tight_layout()
    plt.savefig(f'outputs/figures/reachability_seed{seed}.png',dpi=600)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot temporally reachable nodes vs Δt for each dairy network.'
    )
    parser.add_argument(
        'seed',
        type=int,
        help='Simulation seed (will be shown in plot title and used to find CSV file)'
    )
    args = parser.parse_args()
    plot_reachability_vs_deltaT(args.seed)

