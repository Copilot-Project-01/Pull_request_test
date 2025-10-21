#!/usr/bin/env python3
"""
Script to sum the first 10 odd numbers.
The first 10 odd numbers are: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19
"""

def sum_first_n_odd_numbers(n):
    """
    Calculate the sum of the first n odd numbers.
    
    Args:
        n (int): Number of odd numbers to sum
    
    Returns:
        int: Sum of the first n odd numbers
    """
    total = 0
    for i in range(n):
        odd_number = 2 * i + 1
        total += odd_number
    return total


if __name__ == "__main__":
    # Sum the first 10 odd numbers
    n = 10
    result = sum_first_n_odd_numbers(n)
    
    print(f"The first {n} odd numbers are:", end=" ")
    odd_numbers = [2 * i + 1 for i in range(n)]
    print(", ".join(map(str, odd_numbers)))
    
    print(f"The sum of the first {n} odd numbers is: {result}")
