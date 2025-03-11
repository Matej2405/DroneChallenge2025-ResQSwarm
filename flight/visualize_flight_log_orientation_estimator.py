import matplotlib.pyplot as plt
import re


def parse_flight_log(file_path):
    """Parse the flight log to extract time, pitch, roll, and yaw."""
    time = []
    pitch = []
    roll = []
    yaw = []

    with open(file_path, 'r') as file:
        for line in file:
            # Skip the header or non-orientation lines
            if not line.startswith("Time_ms"):
                match = re.match(r"(\d+),Orientation: pitch=([\d.-]+), roll=([\d.-]+), yaw=([\d.-]+)", line)
                if match:
                    time.append(int(match.group(1)))
                    pitch.append(float(match.group(2)))
                    roll.append(float(match.group(3)))
                    yaw.append(float(match.group(4)))

    return time, pitch, roll, yaw


def plot_orientation(time, pitch, roll, yaw):
    """Plot the roll, pitch, and yaw over time."""
    plt.figure(figsize=(10, 6))

    plt.plot(time, pitch, label="Pitch", linewidth=2)
    plt.plot(time, roll, label="Roll", linewidth=2)
    plt.plot(time, yaw, label="Yaw", linewidth=2)

    plt.title("Orientation Over Time", fontsize=16)
    plt.xlabel("Time (ms)", fontsize=14)
    plt.ylabel("Angle (°)", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    # Specify the flight log file path
    log_file = "flight_log.txt"

    # Parse the log file
    time, pitch, roll, yaw = parse_flight_log(log_file)

    # Plot the orientation data
    plot_orientation(time, pitch, roll, yaw)
