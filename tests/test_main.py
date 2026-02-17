import numpy as np
import pytest

from main import Component, RotorCase, calculate_center_of_mass, simulate_case


def test_center_of_mass_is_weighted_average():
    components = (
        Component("a", 1.0, np.array([0.0, 0.0, 0.0])),
        Component("b", 3.0, np.array([2.0, 0.0, 0.0])),
    )
    center_of_mass, total_mass = calculate_center_of_mass(components)
    assert total_mass == pytest.approx(4.0)
    assert center_of_mass[0] == pytest.approx(1.5)
    assert center_of_mass[1] == pytest.approx(0.0)
    assert center_of_mass[2] == pytest.approx(0.0)


def test_balanced_case_produces_lower_force_than_unbalanced_case():
    omega = 2 * np.pi * 10
    time = np.linspace(0.0, 2.0, 1000)

    balanced = RotorCase(
        name="balanced",
        components=(
            Component("a", 1.0, np.array([1.0, 0.0, 0.0])),
            Component("b", 1.0, np.array([-1.0, 0.0, 0.0])),
        ),
    )
    unbalanced = RotorCase(
        name="unbalanced",
        components=(
            Component("a", 1.0, np.array([1.0, 0.0, 0.0])),
            Component("b", 1.0, np.array([0.0, 0.0, 0.0])),
        ),
    )

    balanced_result = simulate_case(balanced, omega, time)
    unbalanced_result = simulate_case(unbalanced, omega, time)

    assert balanced_result.radial_offset_m < unbalanced_result.radial_offset_m
    assert balanced_result.centrifugal_force_n < unbalanced_result.centrifugal_force_n


def test_component_validates_negative_mass():
    with pytest.raises(ValueError):
        Component("bad", -1.0, np.array([0.0, 0.0, 0.0]))
