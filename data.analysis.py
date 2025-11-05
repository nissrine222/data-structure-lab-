import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define file paths
participant_info_path = r"C:\Users\lenovo\OneDrive\Desktop\data project\participant_info.csv"
data_folder = r"C:\Users\lenovo\OneDrive\Desktop\data project\data"
output_folder = r"C:\Users\lenovo\OneDrive\Desktop\data project\output"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load participant data
try:
    participant_info = pd.read_csv(participant_info_path)
    print("Participant information loaded successfully.")
except Exception as e:
    raise RuntimeError(f"Failed to load participant info: {e}")

# List all CSV files in the data folder
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {data_folder}.")
print(f"Found {len(csv_files)} CSV files in the data folder.")

# Handle missing values in participant_info
participant_info = participant_info.fillna({'MEDICAL_HISTORY': 'Unknown', 'Sleep_Disorders': 'Unknown'})

# Function to resample signals
def resample_signals(df):
    if 'TIMESTAMP' in df.columns:
        try:
            df['TIMESTAMP'] = pd.to_timedelta(df['TIMESTAMP'], unit='s')
            df.set_index('TIMESTAMP', inplace=True)
            numeric_df = df.select_dtypes(include=[np.number])
            resampled_df = numeric_df.resample('15ms').mean().interpolate(method='linear')
            resampled_df.reset_index(inplace=True)
            return resampled_df
        except Exception as e:
            print(f"Error resampling signals: {e}")
            return pd.DataFrame()
    else:
        print("'TIMESTAMP' column not found in dataframe.")
        return pd.DataFrame()

# Function to save plots
def save_plot(fig, filename):
    """
    Saves a plot to the output folder and ensures it does not block subsequent plots.
    """
    filepath = os.path.join(output_folder, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)  # Correctly close the figure
    print(f"Plot saved at: {filepath}")


# Function to plot data with a limited legend
def plot_data(x, y, label, title, filename, color):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x, y, label=label, color=color)
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel(label)
    ax.legend(loc='lower left')
    ax.grid()
    save_plot(fig, filename)

# Process data files and collect statistics
all_stats_list = []

for data_file_name in csv_files:
    data_file_path = os.path.join(data_folder, data_file_name)
    stats_file_path = os.path.join(output_folder, f"stats_{data_file_name}.csv")
    
    if os.path.exists(stats_file_path):
        print(f"Skipping {data_file_name}, statistics already processed.")
        continue
    
    try:
        data = pd.read_csv(data_file_path)
        numeric_columns = ['IBI', 'Obstructive_Apnea', 'Central_Apnea', 'Hypopnea', 'Multiple_Events', 'HR']
        for column in numeric_columns:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors='coerce')

        for col in numeric_columns:
            if col in data.columns:
                if not data[col].isna().all():
                    data[col].fillna(data[col].mean() if col == 'IBI' else data[col].median(), inplace=True)
                else:
                    print(f"Column '{col}' is empty or all NaN. Filling with 0.")
                    data[col] = 0

        data_resampled = resample_signals(data)
        stats = data_resampled.describe()
        all_stats_list.append(stats)
        stats.to_csv(stats_file_path)

        # Bar Plot - Mean Values
        available_columns = ['HR', 'IBI', 'Obstructive_Apnea', 'Central_Apnea', 'Hypopnea']
        available_columns = list(set(available_columns) & set(data_resampled.columns))
        if available_columns:
            mean_values = data_resampled[available_columns].mean()
            fig, ax = plt.subplots(figsize=(12, 6))
            mean_values.plot(kind='bar', color='lightblue', ax=ax)
            ax.set_title(f"Mean Values of Metrics - {data_file_name}")
            ax.set_ylabel("Mean Value")
            ax.set_xlabel("Metrics")
            save_plot(fig, f"{data_file_name}_mean_values.png")

            # Box Plot
            fig, ax = plt.subplots(figsize=(12, 6))
            data_resampled[available_columns].plot(kind='box', ax=ax)
            ax.set_title(f"Boxplot of Metrics - {data_file_name}")
            ax.set_ylabel("Value")
            save_plot(fig, f"{data_file_name}_boxplot.png")
            
             # Plot BVP
        if 'BVP' in data_resampled.columns:
            plot_data(data_resampled['TIMESTAMP'], data_resampled['BVP'], 
                      'Blood Volume Pulse (BVP)', 
                      f'BVP Over Time - {data_file_name}', 
                      f'{data_file_name}_BVP.png', 
                      'purple')

        # Plot Heart Rate
        if 'HR' in data_resampled.columns:
            plot_data(data_resampled['TIMESTAMP'], data_resampled['HR'], 
                      'Heart Rate', 
                      f'Heart Rate Over Time - {data_file_name}', 
                      f'{data_file_name}_HR.png', 
                      'pink')
            
    except Exception as e:
        print(f"Error processing {data_file_name}: {e}")

# Combine all statistics into a single CSV
if all_stats_list:
    combined_stats_path = os.path.join(output_folder, "combined_physiology_statistics.csv")
    pd.concat(all_stats_list).to_csv(combined_stats_path, index=False)
    print("Combined physiological statistics saved.")

# Save demographic statistics
demographics_stats = participant_info.describe(include='all')
demographics_stats.to_csv(os.path.join(output_folder, "demographics_statistics.csv"))
print("Demographics statistics saved.")

# Compare sleep disorder groups
def compare_sleep_disorder_groups(participant_info):
    if 'Sleep_Disorders' in participant_info.columns:
        grouped_data = participant_info.groupby('Sleep_Disorders').mean(numeric_only=True)
        available_metrics = set(grouped_data.columns) & {'AGE', 'BMI', 'OAHI', 'AHI', 'Mean_SaO2', 'Arousal Index'}
        if not available_metrics:
            print("No relevant metrics available for comparison in the dataset.")
            return
        
        comparison_stats = grouped_data[list(available_metrics)]
        fig, ax = plt.subplots(figsize=(12, 6))  # Create Figure and Axes
        comparison_stats.T.plot(kind='bar', ax=ax, colormap='viridis', edgecolor='black')
        ax.set_title("Comparison of Metrics Between Sleep Disorder Groups")
        ax.set_ylabel("Average Value")
        ax.set_xlabel("Metrics")
        ax.set_xticklabels(ax.get_xticks(), rotation=45)
        ax.grid(axis='y')
        ax.legend(title="Sleep Disorder", bbox_to_anchor=(1.05, 1), loc='upper left')
        save_plot(fig, "comparison_sleep_disorders.png")  # Save using Figure
    else:
        print("Sleep disorder data not found.")

# Generate correlation heatmap
def plot_correlation_heatmap(data):
    numeric_data = data.select_dtypes(include=[np.number])
    if not numeric_data.empty:
        correlation_matrix = numeric_data.corr()
        fig, ax = plt.subplots(figsize=(10, 8))  # Create Figure and Axes
        sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True, linewidths=0.5, ax=ax)
        ax.set_title("Correlation Heatmap")
        save_plot(fig, "correlation_heatmap.png")  # Save using Figure
    else:
        print("No numeric data available for correlation heatmap.")

# Execute group comparison and correlation heatmap
compare_sleep_disorder_groups(participant_info)
plot_correlation_heatmap(participant_info)

print("Analysis complete. Resampled data, statistics, and plots saved.")
