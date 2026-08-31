from .core.config import get_config_path
from .core.data import Data
from .core.dummy import DummyVisualizer
from .core.runner import load_datasets, next_data, reset, run_visualizer, running, set_action
from .visualizers.array import (
    BinarySearchVisualizer,
    BinaryTreeArrayVisualizer,
    BubbleSortVisualizer,
    CountSortVisualizer,
    FindMaxVisualizer,
    HeapSortVisualizer,
    InsertionSortVisualizer,
    MergeBattleVisualizer,
    MergeSortVisualizer,
    QuickSortVisualizer,
    RadixLsdVisualizer,
    RadixMsdWordsVisualizer,
    SequentialSearchVisualizer,
    SelectionSortVisualizer,
    ShellSortVisualizer,
    VerticalBubbleSortVisualizer,
)
from .visualizers.euler import EulerCircuitVisualizer
from .visualizers.knight import KnightsTourVisualizer


def visualizer(name, enabled=True):
    reset()
    if not enabled:
        return DummyVisualizer()
    if name == "find_max":
        return FindMaxVisualizer("Find Max")
    if name == "search_seq":
        return SequentialSearchVisualizer("Sequential Search")
    if name == "search_bin":
        return BinarySearchVisualizer("Binary Search")
    if name == "bubble_sort":
        return BubbleSortVisualizer("Bubble Sort")
    if name == "bubble_sort_vertical":
        return VerticalBubbleSortVisualizer("Bubble Sort")
    if name == "selection_sort":
        return SelectionSortVisualizer("Selection Sort")
    if name == "insertion_sort":
        return InsertionSortVisualizer("Insertion Sort")
    if name == "shell_sort":
        return ShellSortVisualizer("Shell Sort")
    if name == "merge_sort":
        return MergeSortVisualizer("Merge Sort")
    if name == "merge_battle":
        return MergeBattleVisualizer("Merge Battle")
    if name == "quick_sort":
        return QuickSortVisualizer("Quick Sort")
    if name == "quick_sort_partition":
        return QuickSortVisualizer("Quick Sort: Partition").set_fine_sections(True)
    if name == "binary_tree_array":
        return BinaryTreeArrayVisualizer("Binary Tree in Array")
    if name == "heap_sort":
        return HeapSortVisualizer("Heap Sort")
    if name == "count_sort":
        return CountSortVisualizer("Count Sort")
    if name == "radix_lsd":
        return RadixLsdVisualizer("Radix Sort: LSD")
    if name == "radix_msd_words":
        return RadixMsdWordsVisualizer("Radix Sort: MSD")
    if name == "euler":
        return EulerCircuitVisualizer("Euler Circuit")
    if name == "knights_tour":
        return KnightsTourVisualizer("Knight's Tour")
    return DummyVisualizer()


def test_func():
    return "pyvisalgo is installed"


__all__ = [
    "DummyVisualizer",
    "Data",
    "BubbleSortVisualizer",
    "BinarySearchVisualizer",
    "BinaryTreeArrayVisualizer",
    "CountSortVisualizer",
    "EulerCircuitVisualizer",
    "FindMaxVisualizer",
    "HeapSortVisualizer",
    "InsertionSortVisualizer",
    "KnightsTourVisualizer",
    "MergeSortVisualizer",
    "MergeBattleVisualizer",
    "QuickSortVisualizer",
    "RadixLsdVisualizer",
    "RadixMsdWordsVisualizer",
    "SequentialSearchVisualizer",
    "SelectionSortVisualizer",
    "ShellSortVisualizer",
    "VerticalBubbleSortVisualizer",
    "get_config_path",
    "load_datasets",
    "next_data",
    "reset",
    "run_visualizer",
    "running",
    "set_action",
    "test_func",
    "visualizer",
]
