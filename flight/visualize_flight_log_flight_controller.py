import matplotlib.pyplot as plt
import re


def parse_flight_log(file_path):
    """
    Parse the flight log to extract time, angles, PID outputs, and motor throttles.
    Expected format:
    time_ms, pitch, roll, yaw, pid_pitch, pid_roll, pid_yaw, front_left, rear_left, front_right, rear_right
    """
    time = []
    pitch, roll, yaw = [], [], []
    pid_pitch, pid_roll, pid_yaw = [], [], []
    throttle_front_left, throttle_rear_left, throttle_front_right, throttle_rear_right = [], [], [], []

    with open(file_path, 'r') as file:
        for line in file:
            # Match lines with the specified numerical format
            match = re.match(
                r"(\d+),([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+),([\d.-]+)",
                line.strip()
            )
            if match:
                # Extract data
                time.append(int(match.group(1)))
                pitch.append(float(match.group(2)))
                roll.append(float(match.group(3)))
                yaw.append(float(match.group(4)))
                pid_pitch.append(float(match.group(5)))
                pid_roll.append(float(match.group(6)))
                pid_yaw.append(float(match.group(7)))
                throttle_front_left.append(float(match.group(8)))
                throttle_rear_left.append(float(match.group(9)))
                throttle_front_right.append(float(match.group(10)))
                throttle_rear_right.append(float(match.group(11)))

    return time, (pitch, roll, yaw), (pid_pitch, pid_roll, pid_yaw), (
        throttle_front_left,
        throttle_rear_left,
        throttle_front_right,
        throttle_rear_right,
    )


def plot_flight_log(time, angles, pid_outputs, motor_throttles):
    """Create a plot with three subplots for angles, PID outputs, and motor throttles."""
    pitch, roll, yaw = angles
    pid_pitch, pid_roll, pid_yaw = pid_outputs
    throttle_front_left, throttle_rear_left, throttle_front_right, throttle_rear_right = motor_throttles

    # Create subplots
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    # Measured Angles
    axs[0].plot(time, pitch, label="Pitch", linewidth=2)
    axs[0].plot(time, roll, label="Roll", linewidth=2)
    axs[0].plot(time, yaw, label="Yaw", linewidth=2)
    axs[0].set_title("Measured Angles")
    axs[0].set_ylabel("Angle (°)")
    axs[0].legend()
    axs[0].grid(True)

    # PID Outputs
    axs[1].plot(time, pid_pitch, label="PID Pitch", linewidth=2)
    axs[1].plot(time, pid_roll, label="PID Roll", linewidth=2)
    axs[1].plot(time, pid_yaw, label="PID Yaw", linewidth=2)
    axs[1].set_title("PID Outputs")
    axs[1].set_ylabel("PID Value")
    axs[1].legend()
    axs[1].grid(True)

    # Motor Throttles
    axs[2].plot(time, throttle_front_left, label="Front Left", linewidth=2)
    axs[2].plot(time, throttle_rear_left, label="Rear Left", linewidth=2)
    axs[2].plot(time, throttle_front_right, label="Front Right", linewidth=2)
    axs[2].plot(time, throttle_rear_right, label="Rear Right", linewidth=2)
    axs[2].set_title("Motor Throttles")
    axs[2].set_xlabel("Time (ms)")
    axs[2].set_ylabel("Throttle")
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Specify the log file path
    log_file = "flight_log.txt"

    # Parse the log file
    time, angles, pid_outputs, motor_throttles = parse_flight_log(log_file)

    # Plot the data
    plot_flight_log(time, angles, pid_outputs, motor_throttles)
