from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class Component:
    """A single rigid component mounted on a rotating body."""

    name: str
    mass_kg: float
    position_m: np.ndarray

    def __post_init__(self) -> None:
        if self.mass_kg <= 0:
            raise ValueError(f"{self.name}: mass must be > 0 kg.")

        position = np.asarray(self.position_m, dtype=float)
        if position.shape != (3,):
            raise ValueError(f"{self.name}: position must be a 3D vector [x, y, z].")

        object.__setattr__(self, "position_m", position)


@dataclass(frozen=True)
class RotorCase:
    """A named configuration of components."""

    name: str
    components: tuple[Component, ...]


@dataclass(frozen=True)
class CaseResult:
    """Computed outputs for one rotor configuration."""

    name: str
    total_mass_kg: float
    center_of_mass_m: np.ndarray
    radial_offset_m: float
    centrifugal_force_n: float
    vibration_signal_m: np.ndarray


def calculate_center_of_mass(components: Sequence[Component]) -> tuple[np.ndarray, float]:
    """Return center of mass and total mass for a set of components."""
    if not components:
        raise ValueError("At least one component is required.")

    masses = np.array([component.mass_kg for component in components], dtype=float)
    positions = np.array([component.position_m for component in components], dtype=float)
    total_mass = float(masses.sum())
    center_of_mass = (masses[:, np.newaxis] * positions).sum(axis=0) / total_mass
    return center_of_mass, total_mass


def simulate_case(case: RotorCase, omega_rad_s: float, time_s: np.ndarray) -> CaseResult:
    """
    Compute vibration proxy metrics for one case.

    This model uses COM radial offset as a simple sinusoidal displacement proxy.
    """
    center_of_mass, total_mass = calculate_center_of_mass(case.components)
    radial_offset = float(np.linalg.norm(center_of_mass[:2]))
    centrifugal_force = total_mass * omega_rad_s**2 * radial_offset
    vibration_signal = radial_offset * np.sin(omega_rad_s * time_s)

    return CaseResult(
        name=case.name,
        total_mass_kg=total_mass,
        center_of_mass_m=center_of_mass,
        radial_offset_m=radial_offset,
        centrifugal_force_n=float(centrifugal_force),
        vibration_signal_m=vibration_signal,
    )


def build_default_cases() -> tuple[RotorCase, RotorCase]:
    """Create baseline balanced and unbalanced examples."""
    unbalanced = RotorCase(
        name="Unbalanced",
        components=(
            Component("component1", 2.0, np.array([1.0, 2.0, 0.0])),
            Component("component2", 1.5, np.array([-1.0, -2.0, 0.0])),
            Component("component3", 2.5, np.array([2.0, 1.0, 0.0])),
        ),
    )
    balanced = RotorCase(
        name="Balanced",
        components=(
            Component("component1", 2.0, np.array([1.0, 0.0, 0.0])),
            Component("component2", 1.5, np.array([-1.0, 0.0, 0.0])),
            Component("component3", 2.5, np.array([0.0, 0.0, 0.0])),
        ),
    )
    return unbalanced, balanced


def plot_vibration_comparison(time_s: np.ndarray, results: Sequence[CaseResult]) -> plt.Figure:
    """Plot displacement proxy signal for each case."""
    figure, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 5), sharey=True)
    if len(results) == 1:
        axes = [axes]

    for axis, result in zip(axes, results):
        axis.plot(time_s, result.vibration_signal_m)
        axis.set_title(f"{result.name} Vibration Proxy")
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Displacement proxy (m)")
        axis.grid(True)

    figure.tight_layout()
    return figure


def print_summary(results: Sequence[CaseResult], rpm: float) -> None:
    """Print concise, comparable metrics for all cases."""
    print(f"Simulation speed: {rpm:.1f} RPM\n")
    for result in results:
        com = np.array2string(result.center_of_mass_m, precision=4, suppress_small=True)
        print(f"{result.name}:")
        print(f"  Total mass: {result.total_mass_kg:.3f} kg")
        print(f"  Center of mass: {com} m")
        print(f"  Radial COM offset: {result.radial_offset_m:.6f} m")
        print(f"  Centrifugal force: {result.centrifugal_force_n:.2f} N")
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare how rotor mass balance affects vibration proxy and centrifugal force."
    )
    parser.add_argument("--rpm", type=float, default=600.0, help="Rotational speed in RPM.")
    parser.add_argument("--duration", type=float, default=2.0, help="Simulation duration in seconds.")
    parser.add_argument("--samples", type=int, default=1000, help="Number of time samples.")
    parser.add_argument(
        "--save-plot",
        type=str,
        default="axis_comparison.png",
        help="Output path for the comparison figure.",
    )
    parser.add_argument("--no-show", action="store_true", help="Skip opening the interactive plot window.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.rpm <= 0:
        raise ValueError("RPM must be > 0.")
    if args.duration <= 0:
        raise ValueError("Duration must be > 0 seconds.")
    if args.samples < 2:
        raise ValueError("Samples must be >= 2.")

    omega_rad_s = args.rpm * (2 * np.pi / 60.0)
    time_s = np.linspace(0.0, args.duration, args.samples)

    cases = build_default_cases()
    results = tuple(simulate_case(case, omega_rad_s, time_s) for case in cases)
    print_summary(results, args.rpm)

    figure = plot_vibration_comparison(time_s, results)
    if args.save_plot:
        figure.savefig(args.save_plot, dpi=150)
        print(f"Saved plot: {args.save_plot}")
    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
