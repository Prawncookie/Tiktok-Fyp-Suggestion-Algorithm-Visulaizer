import matplotlib.pyplot as plt
import random
import time
import numpy as np

# Configuration settings for the TikTok FYP simulator
CONFIG = {
    'like_bonus': 50,      # Points added for each liked video
    'share_bonus': 100,    # Points added for each shared video
    'initial_recs': 6,     # Number of videos to recommend initially
    'video_pool_size': 20, # Total number of videos in the pool
    'min_watch_time': 10,  # Minimum watch time in seconds
    'max_watch_time': 60   # Maximum watch time in seconds
}

users_data = {
    'Alice': {
        'watched': [(1, 40), (3, 60), (2, 20), (6, 50), (10, 60), (13, 10)],
        'likes': [10, 6, 3],
        'shares': [3],
    },
    'Liam': {
        'watched': [(20, 40), (5, 10), (18, 20), (1, 30), (13, 20), (17, 10)],
        'likes': [1, 20],
        'shares': [],
    },
    'Bob': {
        'watched': [(4, 30), (10, 20), (15, 30), (7, 20), (12, 50), (3, 10)],
        'likes': [4, 12, 7, 15],
        'shares': [10, 12, 4],
    },
    'Travis': {
        'watched': [(8, 20), (13, 40), (11, 30), (6, 50), (9, 20), (8, 30)],
        'likes': [13, 8],
        'shares': [8, 6, 13],
    },
    'Scott': {
        'watched': [(17, 40), (16, 20), (19, 20), (14, 40), (2, 30), (15, 20)],
        'likes': [],
        'shares': [],
    }
}
def calculate_engagement(user_data):
    # Step 1: Add up all watch times
    total_watch_time = 0
    for video_id, watch_time in user_data['watched']:
        total_watch_time += watch_time
    
    # Step 2: Calculate like bonus
    like_bonus = len(user_data['likes']) * CONFIG['like_bonus']
    
    # Step 3: Calculate share bonus
    share_bonus = len(user_data['shares']) * CONFIG['share_bonus']
    
    # Step 4: Return total
    return total_watch_time + like_bonus + share_bonus

alice_score = calculate_engagement(users_data['Alice'])
print(f"Alice's engagement score: {alice_score}")

bob_score = calculate_engagement(users_data['Bob'])
print(f"Bob's engagement score: {bob_score}")