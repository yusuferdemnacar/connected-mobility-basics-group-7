import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from load_data import Message, Hop # Hop is needed, otherwise the pickle load won't work

# Disclaimer: Claude 4.0 helped writing this code, especially in plotting. 
# Data processing and loading was done by us

def plot_hop_counts(df):
    """Plot hop count distributions for each message size using a grouped bar plot"""
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Get unique sizes and create color map
    sizes = sorted(df['Size'].unique())
    colors = plt.cm.tab10(np.linspace(0, 1, len(sizes)))
    
    # Get unique hop counts that actually exist in the data
    unique_hop_counts = sorted(df['Hop_Count'].unique())
    
    # Width of each bar and positions of bar groups
    bar_width = 0.8 / len(sizes)  # Adjust total width of group
    
    # Store frequencies for statistics
    all_frequencies = {}
    
    # Plot bars for each size
    for i, size in enumerate(sizes):
        size_data = df[df['Size'] == size]['Hop_Count']
        
        # Calculate frequencies
        unique, counts = np.unique(size_data, return_counts=True)
        freq_pct = (counts / len(size_data)) * 100
        all_frequencies[size] = dict(zip(unique, freq_pct))
        
        # Calculate bar positions using actual hop count values
        x = np.array(unique_hop_counts) + i * bar_width - (len(sizes)-1) * bar_width/2
        
        # Create frequency array matching unique_hop_counts
        freq_array = np.zeros(len(unique_hop_counts))
        for j, hop_count in enumerate(unique_hop_counts):
            freq_array[j] = all_frequencies[size].get(hop_count, 0)
        
        # Plot bars
        bars = ax.bar(x, freq_array, bar_width, 
                     label=f'{int(size)} bytes',
                     color=colors[i],
                     alpha=0.7)
        
        # Add value labels on top of bars
        for bar, freq in zip(bars, freq_array):
            if freq > 0:  # Only add label if there's a non-zero frequency
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{freq:.1f}%',
                       ha='center', va='bottom',
                       rotation=90,
                       fontsize=8)
    
    # Add mean hop count for each size in text box
    text_str = "Mean Hop Counts:\n"
    for size in sizes:
        size_data = df[df['Size'] == size]['Hop_Count']
        mean_hops = size_data.mean()
        std_hops = size_data.std()
        text_str += f"{int(size)} bytes: {mean_hops:.2f} ± {std_hops:.2f}\n"
    
    # Position the text box in the upper right corner
    ax.text(0.95, 0.95, text_str,
            transform=ax.transAxes,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Customize plot
    ax.set_xlabel('Hop Count')
    ax.set_ylabel('Frequency (%)')
    ax.set_title('Hop Count Distribution by Message Size')
    ax.set_xticks(unique_hop_counts)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'figures/hopcount_distribution_by_size.png', 
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_distance_vs_hopcount_by_size(df, num_bins = 20):
    fig, ax = plt.subplots(figsize=(12, 8))

    for size in sorted(df['Size'].unique()):
        size_data = df[df['Size'] == size]
        
        # Create distance bins
        min_dist = size_data['Distance'].min()
        max_dist = size_data['Distance'].max()
        distance_bins = np.linspace(min_dist, max_dist, num_bins)
        bin_centers = (distance_bins[:-1] + distance_bins[1:]) / 2
        
        mean_hops = []
        std_hops = []
        
        # Calculate mean and std for each bin
        for i in range(len(distance_bins)-1):
            mask = (size_data['Distance'] >= distance_bins[i]) & (size_data['Distance'] < distance_bins[i+1])
            bin_data = size_data[mask]['Hop_Count']
            if len(bin_data) > 0:  # Only include bins with data
                mean_hops.append(bin_data.mean())
                std_hops.append(bin_data.std())
            else:
                mean_hops.append(np.nan)
                std_hops.append(np.nan)
        
        mean_hops = np.array(mean_hops)
        std_hops = np.array(std_hops)
        
        # Remove NaN values for plotting
        valid_mask = ~np.isnan(mean_hops)
        valid_centers = bin_centers[valid_mask]
        valid_means = mean_hops[valid_mask]
        valid_stds = std_hops[valid_mask]
        
        # Plot mean line
        line = ax.plot(valid_centers, valid_means, 
                        label=f'{int(size)} bytes', 
                        linewidth=2)
        
        # Plot standard deviation as shaded area
        ax.fill_between(valid_centers, 
                        valid_means - valid_stds, 
                        valid_means + valid_stds, 
                        alpha=0.2, 
                        color=line[0].get_color())

    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Average Hop Count')
    ax.set_title('Distance vs Average Hop Count by Message Size')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'figures/distance_hopcount_per_size.png', dpi=300, bbox_inches='tight')

def plot_latency_frequency_by_size(messages):
    """Plot percentile distribution of latencies for all message sizes"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sizes = np.unique([msg.size for msg in messages])
    # Get color map for different sizes
    colors = plt.cm.tab10(np.linspace(0, 1, len(sizes)))
    
    for i, size in enumerate(sizes):
        # Filter messages for this size
        messages_for_size = list(filter(lambda msg, s_inner=int(size): 
                                      msg.size == s_inner and msg.delivery_time > 0, 
                                      messages))
        
        if not messages_for_size:
            continue
            
        # Get latencies and sort them
        latencies = sorted([msg.delivery_time for msg in messages_for_size])
        
        # Calculate percentiles
        percentiles = np.arange(1, len(latencies) + 1) / len(latencies) * 100
        
        # Plot percentile distribution
        ax.plot(latencies, percentiles, 
                label=f'{size} bytes', 
                color=colors[i],
                linewidth=2)

    ax.set_xlabel('Latency (seconds)')
    ax.set_ylabel('Percentile (%)')
    ax.set_title('Latency Percentile Distribution')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig(f'figures/latency_percentiles.png')
    plt.close()

def plot_node_degree_vs_latency(messages):
    """Plot relationship between node degree and hop latency aggregated across all message sizes"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create data points for each hop
    data = []
    for msg in messages:
        if msg.hops:
            for hop in msg.hops:
                if hop.hop_time > 0:
                    data.append({
                        'size': msg.size,
                        'node_degree': hop.from_node_degree,
                        'hop_latency': hop.hop_time
                    })
    
    df = pd.DataFrame(data)
    
    # Create binned statistics
    bins = np.arange(0, 51, 5)  # 0-50 in steps of 5
    bin_means = []
    bin_stds = []
    bin_centers = []
    bin_counts = []
    
    for j in range(len(bins)-1):
        mask = (df['node_degree'] >= bins[j]) & (df['node_degree'] < bins[j+1])
        if mask.any():
            bin_means.append(df[mask]['hop_latency'].mean())
            bin_stds.append(df[mask]['hop_latency'].std())
            bin_centers.append((bins[j] + bins[j+1]) / 2)
            bin_counts.append(len(df[mask]))
    
    bin_means = np.array(bin_means)
    bin_stds = np.array(bin_stds)
    bin_centers = np.array(bin_centers)
    
    # Plot mean line and standard deviation band
    ax.plot(bin_centers, bin_means,
            color='blue',
            linewidth=2.5)
    
    ax.fill_between(bin_centers,
                    bin_means - bin_stds,
                    bin_means + bin_stds,
                    alpha=0.2,
                    color='blue')
    
    # Set more frequent y-axis ticks (every 25 seconds)
    max_y = max(bin_means + bin_stds) + 25  # Add some padding
    y_ticks = np.arange(0, max_y, 25)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{y:.0f}' for y in y_ticks])
    
    # Customize plot
    ax.set_xlabel('Node Degree')
    ax.set_ylabel('Hop Latency (s)')
    ax.set_title('Node Degree vs Hop Latency (All Message Sizes)')
    ax.grid(True, alpha=0.3)
    
    # Add statistics in text box
    stats_text = "Statistics:\n"
    stats_text += f"Total hops: {len(df):,}\n"
    stats_text += f"Mean latency: {df['hop_latency'].mean():.2f}s\n\n"
    stats_text += "By node degree range:\n"
    
    degree_ranges = [(0, 10), (11, 20), (21, 30), (31, 40), (41, 50)]
    for min_deg, max_deg in degree_ranges:
        mask = (df['node_degree'] >= min_deg) & (df['node_degree'] <= max_deg)
        if mask.any():
            mean_lat = df[mask]['hop_latency'].mean()
            std_lat = df[mask]['hop_latency'].std()
            count = mask.sum()
            stats_text += f"Degree {min_deg}-{max_deg}:\n"
            stats_text += f"  Mean: {mean_lat:.2f}s\n"
            stats_text += f"  Std Dev: {std_lat:.2f}s\n"
            stats_text += f"  Sample size: {count:,}\n"
    
    # Add sample sizes to plot
    for x, y, count in zip(bin_centers, bin_means, bin_counts):
        ax.text(x, y + bin_stds[bin_centers == x][0], 
                f'n={count:,}',
                ha='center', va='bottom',
                fontsize=8)
    
    ax.text(1.05, 0.5, stats_text,
            transform=ax.transAxes,
            verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'figures/node_degree_vs_hoplatency_aggregate.png',
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_data_quality_analysis(messages: list[Message]):
    data = {
        'Distance': [msg.distance for msg in messages],
        'Size': [msg.size for msg in messages],
        'Hop_Count': [len(msg.hops) for msg in messages],
        'Latency': [msg.delivery_time for msg in messages]
    }
    df = pd.DataFrame(data)
    
    plot_hop_counts(df)
    plot_distance_vs_hopcount_by_size(df, num_bins=20)
    plot_latency_frequency_by_size(messages)
    plot_node_degree_vs_latency(messages)

def plot_correlation_heatmap(messages: list[Message]):
    data = []
    for msg in messages:
        if msg.hops:
            for hop in msg.hops:
                data.append({
                    'Message_Size': msg.size,
                    'Total_Distance': msg.distance,
                    'Total_Hops': len(msg.hops),
                    'Total_Latency': msg.delivery_time,
                    'Hop_Latency': hop.hop_time,
                    'Node_Degree': hop.from_node_degree,
                })
    
    df = pd.DataFrame(data)
    
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    
    correlation_matrix = df.corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(correlation_matrix.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    cbar = plt.colorbar(im)
    cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)
    
    # Set ticks and labels
    ax.set_xticks(range(len(correlation_matrix.columns)))
    ax.set_yticks(range(len(correlation_matrix.columns)))
    ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(correlation_matrix.columns)
    
    # Add correlation values as text annotations
    for i in range(len(correlation_matrix.columns)):
        for j in range(len(correlation_matrix.columns)):
            value = correlation_matrix.iloc[i, j]
            color = 'white' if abs(value) > 0.5 else 'black'
            ax.text(j, i, f'{value:.3f}', 
                   ha='center', va='center',
                   color=color, fontweight='bold', 
                   fontsize=10)
    
    plt.title('Correlation Matrix: Network Factors vs Latency', pad=20, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'figures/correlation_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()

def main():
    with open("message.pkl", 'rb') as f:
        messages = pickle.load(f)

    # Filter messages with invalid data
    messages = [msg for msg in messages if msg.size > 0 and msg.distance > 0 and msg.delivery_time > 0]
    
    plot_data_quality_analysis(messages)

    plot_correlation_heatmap(messages)
    
    print("All plots generated successfully!")

if __name__ == "__main__":
    main()