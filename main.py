import numpy as np
import matplotlib.pyplot as plt

def calculate_center_of_mass(components):
    total_mass = sum(comp['mass'] for comp in components.values())
    center_of_mass = sum(comp['mass'] * comp['position'] for comp in components.values()) / total_mass
    return center_of_mass, total_mass

def plot_vibrations(time, vibrations, title):
    plt.plot(time, vibrations)
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (m)')
    plt.grid(True)

# Define the mass and position of each component in the system (unbalanced)
components_unbalanced = {
    'component1': {'mass': 2.0, 'position': np.array([1.0, 2.0, 0.0])},
    'component2': {'mass': 1.5, 'position': np.array([-1.0, -2.0, 0.0])},
    'component3': {'mass': 2.5, 'position': np.array([2.0, 1.0, 0.0])},
    # Add more components as needed
}

# Define the mass and position of each component in the system (balanced)
components_balanced = {
    'component1': {'mass': 2.0, 'position': np.array([1.0, 0.0, 0.0])},
    'component2': {'mass': 1.5, 'position': np.array([-1.0, 0.0, 0.0])},
    'component3': {'mass': 2.5, 'position': np.array([0.0, 0.0, 0.0])},
    # Add more components as needed
}

# Calculate the center of mass for both configurations
center_of_mass_unbalanced, total_mass_unbalanced = calculate_center_of_mass(components_unbalanced)
center_of_mass_balanced, total_mass_balanced = calculate_center_of_mass(components_balanced)

# Parameters for simulation
omega = 2 * np.pi * 10  # rotational speed in rad/s (example value, can be changed)
time = np.linspace(0, 2, 1000)

# Unbalanced case
radius_unbalanced = np.linalg.norm(center_of_mass_unbalanced[:2])
centrifugal_force_unbalanced = total_mass_unbalanced * omega**2 * radius_unbalanced
vibrations_unbalanced = radius_unbalanced * np.sin(omega * time)

# Balanced case
radius_balanced = np.linalg.norm(center_of_mass_balanced[:2])
centrifugal_force_balanced = total_mass_balanced * omega**2 * radius_balanced
vibrations_balanced = radius_balanced * np.sin(omega * time)

# Plot the vibrations for both cases
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plot_vibrations(time, vibrations_unbalanced, 'Unbalanced System Vibrations')
plt.subplot(1, 2, 2)
plot_vibrations(time, vibrations_balanced, 'Balanced System Vibrations')

plt.tight_layout()
plt.show()

# Print results
print("Unbalanced System:")
print("Center of Mass:", center_of_mass_unbalanced)
print(f"Centrifugal Force: {centrifugal_force_unbalanced:.2f} N")

print("\nBalanced System:")
print("Center of Mass:", center_of_mass_balanced)
print(f"Centrifugal Force: {centrifugal_force_balanced:.2f} N")
