<img width="1200" height="400" alt="image" src="https://github.com/user-attachments/assets/4161cee1-772f-4784-8afb-b75fe606770b" />

Overview
The TikTok FYP Suggestion Algorithm Visualizer is an open-source tool designed to simulate and visualize the mechanics of TikTok's "For You Page" (FYP) recommendation system. This project models key aspects of content discovery, user interactions, and algorithm adaptation, providing insights into how content virality and personalization evolve over time. It is built in Python and serves as an educational resource for developers, researchers, and content creators interested in recommendation systems.
The simulator incorporates collaborative filtering principles, engagement scoring, phase-based learning (discovery, personalization, adaptation), and visualization tools to demonstrate real-world dynamics in a controlled environment. It was developed as part of a software engineering project to emulate TikTok's math-driven recommendation logic, as described by TikTok CEO Shou Zi Chew in 2025 interviews, where the algorithm uses user engagement patterns (likes, shares, watch time) to refine suggestions.
Features

Simulation Engine: Models TikTok's FYP, capturing content diversity and user engagement across multiple phases.
Dynamic Content Pool: Creates a realistic environment for content and user interaction simulation, with a pool of 60 videos across 5 categories (cooking, dance, comedy, pets, sports).
Data Visualization: Utilizes Matplotlib for insightful analysis of algorithm behavior, including user engagement by phase, top viral videos, and category dominance.
Algorithm Insights: Explores how engagement metrics influence content popularity, with analytics on phase metrics, video performance, and overall effectiveness.
Research & Development: Facilitates experimentation with recommendation algorithms and content strategies, including configurable parameters for viral thresholds, exploration rates, and phase transitions.

Installation
Prerequisites
This project requires the following dependencies:

Programming Language: Python 3.8 or higher
Package Manager: pip (included with Python)

No additional external package managers like npm are required, as the project is pure Python.

Steps
1. Clone the Repository:
<img width="1424" height="143" alt="Screenshot 2025-10-02 003104" src="https://github.com/user-attachments/assets/b61b8b77-23a0-4552-83e1-e5949b97a414" />

2 .Navigate to the Project Directory:
<img width="1400" height="188" alt="Screenshot 2025-09-30 021146" src="https://github.com/user-attachments/assets/43c467da-a6f7-4bf4-95de-73734d4d516a" />
3. Install Dependencies:
<img width="1404" height="174" alt="Screenshot 2025-09-30 021257" src="https://github.com/user-attachments/assets/994ca34c-7b51-4174-a4aa-a798fd022c5c" />

Usage
Run the project with:
<img width="1409" height="231" alt="Screenshot 2025-09-30 021343" src="https://github.com/user-attachments/assets/189fd3ed-80ab-439b-8a75-e4d6803d82cf" />
This will execute the simulation for 20 users over 50 sessions, generate analytics insights, and produce visualization files (e.g., User1_engagement.png, top_videos.png, category_dominance.png).

Testing
The project includes basic unit tests for core functions. Run the test suite with:
<img width="1395" height="188" alt="Screenshot 2025-09-30 021439" src="https://github.com/user-attachments/assets/90b41d72-ef8b-4701-a22e-1359c648f3f1" />

Development and Challenges:

This project was developed iteratively, focusing on accuracy to TikTok's described algorithm (e.g., math-based pattern matching for recommendations). 
Key challenges included simulating realistic user behavior and ensuring balanced category dominance in viral content.

The Dominance Issue,
One major challenge was category dominance skew, where simulations often resulted in 2-3 categories dominating top virals, leaving others at zero. This stemmed from feedback loops where early random wins in certain categories (e.g., cooking, dance) amplified their rank scores, starving others.
Attempts to Solve

Initial Forcing: Guaranteed 1-2 recs from low-pref (<0.5) categories, but zeros persisted in some runs.

Randomized Ranking: Shuffled initial ranked videos in discovery to avoid bias, improving variability but not eliminating zeros.
Adaptation Boost: Added +100 score boost for low-pref (<0.4) in adaptation phase, but early lock-in limited impact.

Scaling: Increased to 20 users and 50 sessions for more data, which helped but didn't resolve zeros.

What Finally Worked:

The solution was a stronger diversity override: forcing 1 rec from each of the 5 categories per session in personalization and adaptation phases, capped at 6 recs. Combined with a revised dominance metric (total engages per category / total engages overall), this ensured all categories had non-zero dominance (e.g., 0.15-0.25 range) and balanced viral distribution.

Contributing,
Contributions are welcome! Please follow these steps:

Fork the repository.
Create a feature branch (git checkout -b feature/YourFeature).
Commit your changes (git commit -m "Add YourFeature").
Push to the branch (git push origin feature/YourFeature).
Open a Pull Request.

For bugs or feature requests, open an issue with a detailed description.
License
This project is licensed under the MIT License. See the LICENSE file for details.

For questions or collaboration, contact me through the Github messaging system.
Last updated: September 30, 2025.
