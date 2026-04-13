import matplotlib.pyplot as plt
import random
import time
import numpy as np

# Configuration settings for the TikTok FYP simulator
CONFIG = {
    'like_bonus': 50,
    'share_bonus': 100,
    'initial_recs': 6,
    'video_pool_size': 1000,
    'min_watch_time': 5,
    'max_watch_time': 60,
    'viral_threshold': 0.7,
    'exploration_rate': 0.3,
    'discovery_end': 20,
    'adaptation_start': 30
}

categories = ['cooking', 'dance', 'comedy', 'pets', 'sports']

CATEGORY_COLORS = {
    'cooking': '#E07B54',
    'dance':   '#5B8DB8',
    'comedy':  '#F5C842',
    'pets':    '#6DB56D',
    'sports':  '#9B6BB5',
}

def video_pool():
    """Create a pool of videos with categories, titles, base popularity, and initial performance metrics."""
    videos = {}
    for i in range(1, CONFIG['video_pool_size'] + 1):
        category = categories[(i - 1) % len(categories)]
        title = f"{category.capitalize()} Tip #{i}"
        base_popularity = random.randint(50, 100)
        performance = {'avg_completion': 0.0, 'total_engages': 0}
        videos[i] = {'title': title, 'category': category, 'base_popularity': base_popularity, 'performance': performance}
    video_ids = list(videos.keys())
    random.shuffle(video_ids)
    shuffled_videos = {i: videos[i] for i in video_ids}
    
    return shuffled_videos

video_pool_dict = video_pool()


def initialize_users(num_users):
    """Create simulated users with random category preferences and initial empty interactions."""
    users = {}
    for i in range(1, num_users + 1):
        user_id = f'User{i}'
        prefs = {cat: random.uniform(0.1, 0.3) for cat in categories}
        users[user_id] = {
            'interactions': [],
            'category_prefs': prefs,
            'phase': 'discovery'
        }
    return users


def log_interaction(user_id, video_id, watch_time, liked, shared, commented, session):
    """
    Records a user's interaction with a video and updates user preferences and video performance.
    Behavior:
    - Records the interaction in the user's 'interactions' list.
    - Updates video performance metrics via `update_video_performance`.
    - Boosts the user's category preference if engagement thresholds are met.
    - Updates the user's learning phase based on session and configured thresholds.
    """
    global users
    users = initialize_users(20) if 'users' not in globals() else users
    if user_id in users:
        video_category = video_pool_dict[video_id]['category']
        completion = min(watch_time / 60.0, 1.0)
        interaction = {
            'video_id': video_id,
            'watch_time': watch_time,
            'completion': completion,
            'liked': liked,
            'shared': shared,
            'commented': commented,
            'session': session
        }
        users[user_id]['interactions'].append(interaction)
        update_video_performance(video_id, watch_time, liked, shared, commented)
        
        if shared:
            pref_boost = 0.15      # sharing = strongest signal
        elif liked or commented:
            pref_boost = 0.08
        elif watch_time > 30:
            pref_boost = 0.04      # passive watch = weakest signal
        else:
            pref_boost = 0.0
        users[user_id]['category_prefs'][video_category] = min(users[user_id]['category_prefs'][video_category] + pref_boost, 1.0)

        decay_rate = 0.01
        for cat in users[user_id]['category_prefs']:
            if cat != video_category:
                users[user_id]['category_prefs'][cat] = max(
                    users[user_id]['category_prefs'][cat] - decay_rate, 0.0
                )
        
        if session > CONFIG['discovery_end'] and users[user_id]['phase'] == 'discovery': 
            users[user_id]['phase'] = 'personalization'
        elif session > CONFIG['adaptation_start'] and users[user_id]['phase'] == 'personalization':
            users[user_id]['phase'] = 'adaptation'
    return users

def update_video_performance(video_id, watch_time, liked, shared, commented):
    if video_id not in video_pool_dict:
        print(f'Video ID {video_id} not found in video pool.')
        return
    current_perf = video_pool_dict[video_id]['performance']
    old_avg = current_perf['avg_completion']
    old_engages = current_perf['total_engages']
    completion = min(watch_time / 60.0, 1.0)
    avg_completion = (old_avg * old_engages + completion) / (old_engages + 1)
    current_perf['avg_completion'] = avg_completion
    current_perf['total_engages'] += (1 if liked else 0) + (1 if shared else 0) + (1 if commented else 0)
    if avg_completion > CONFIG['viral_threshold']:
        video_pool_dict[video_id]['base_popularity'] *= 1.2  # 20% boost for viral videos

def Overall_Performance_Score(video_id):
    if video_id not in video_pool_dict:
        print(f'Video ID {video_id} not found in video pool.')
        return None
    base_popularity = video_pool_dict[video_id]['base_popularity']
    avg_completion = video_pool_dict[video_id]['performance']['avg_completion']
    total_engages = video_pool_dict[video_id]['performance']['total_engages']
    score = base_popularity + (avg_completion * 100) + total_engages
    return score

def get_video_rank():
    score_pairs = []
    for video_id in video_pool_dict.keys():
        base_popularity = video_pool_dict[video_id]['base_popularity']
        avg_completion = video_pool_dict[video_id]['performance']['avg_completion']
        total_engages = video_pool_dict[video_id]['performance']['total_engages']
        score = base_popularity + (avg_completion * 100) + total_engages
        score_pairs.append((video_id, score))
    sorted_pairs = sorted(score_pairs, key=lambda x: x[1], reverse=True)
    return [pair[0] for pair in sorted_pairs]

def recommend_videos(user_id, session, num_recs):
    """
    Generate video recommendations based on user phase and session.
    
    Args:
        user_id: ID of the user to recommend for
        session: Current session number
        num_recs: Number of recommendations to return
        
    Returns:
        List of recommended video IDs (limited to num_recs)
    """
    global users, video_pool_dict
    
    # Initialize users if needed
    if 'users' not in globals():
        users = initialize_users(20)
    
    phase = users[user_id]['phase']
    ranked_videos = get_video_rank()
    recommendations = []

    # ============ DISCOVERY PHASE ============
    # Random exploration with some ranked videos
    if phase == 'discovery' and session <= CONFIG['discovery_end']:
        random.shuffle(ranked_videos)
        random_count = int(num_recs * CONFIG['exploration_rate'])
        ranked_count = num_recs - random_count
        
        recommendations = ranked_videos[:ranked_count]
        recommendations.extend(random.sample(list(video_pool_dict.keys()), random_count))
    
    # ============ PERSONALIZATION PHASE ============
    # Score videos by user preferences and overall performance
    elif phase == 'personalization' or (session > CONFIG['discovery_end'] and session <= CONFIG['adaptation_start']):
        dominant_cat = max(users[user_id]['category_prefs'], key=users[user_id]['category_prefs'].get)
        dominant_score = users[user_id]['category_prefs'][dominant_cat]

        injected = []
        if dominant_score > 0.6:
            inject_cats = [c for c in categories if c != dominant_cat]
            chosen_inject = random.sample(inject_cats, min(2, len(inject_cats)))
            for cat in chosen_inject:
                cat_vids = [v for v in video_pool_dict if video_pool_dict[v]['category'] == cat]
                if cat_vids:
                    injected.append(random.choice(cat_vids))

        video_scores = []
        for vid in video_pool_dict.keys():
            category = video_pool_dict[vid]['category']
            pref_score = users[user_id]['category_prefs'].get(category, 0.0) * 100
            rank_score = Overall_Performance_Score(vid) or 0
            video_scores.append((vid, pref_score + rank_score))
        
        video_scores.sort(key=lambda x: x[1], reverse=True)
        recommendations = [vid for vid, _ in video_scores[:num_recs]]
        
        # Add diversity: force one recommendation from each category
        diversity_vids = {
            cat: [vid for vid in video_pool_dict 
                  if video_pool_dict[vid]['category'] == cat and vid not in recommendations]
            for cat in categories
        }
        
        diversity_picks = []
        for cat in categories:
            if diversity_vids[cat]:
                diversity_picks.append(random.choice(diversity_vids[cat]))
        
        diversity_picks = diversity_picks[:num_recs]
        merged = diversity_picks + [vid for vid in recommendations if vid not in diversity_picks]
        recommendations = injected + [vid for vid in merged if vid not in injected]
        recommendations = recommendations[:num_recs]

    # ============ ADAPTATION PHASE ============
    # Score with additional boosts for recent interactions and underrepresented categories
    elif phase == 'adaptation' or session > CONFIG['adaptation_start']:
        dominant_cat = max(users[user_id]['category_prefs'], key=users[user_id]['category_prefs'].get)
        dominant_score = users[user_id]['category_prefs'][dominant_cat]

        injected = []
        if dominant_score > 0.6:
            inject_cats = [c for c in categories if c != dominant_cat]
            chosen_inject = random.sample(inject_cats, min(2, len(inject_cats)))
            for cat in chosen_inject:
                cat_vids = [v for v in video_pool_dict if video_pool_dict[v]['category'] == cat]
                if cat_vids:
                    injected.append(random.choice(cat_vids))

        recent_vids = [i['video_id'] for i in users[user_id]['interactions'][-5:]] if users[user_id]['interactions'] else []

        video_scores = []
        for vid in video_pool_dict.keys():
            category = video_pool_dict[vid]['category']
            pref_score = users[user_id]['category_prefs'].get(category, 0.0) * 100
            rank_score = Overall_Performance_Score(vid) or 0
            recent_boost = 50 if vid in recent_vids else 0
            low_pref_boost = 100 if users[user_id]['category_prefs'].get(category, 0.0) < 0.4 else 0
            
            total_score = pref_score + rank_score + recent_boost + low_pref_boost
            video_scores.append((vid, total_score))
        
        video_scores.sort(key=lambda x: x[1], reverse=True)
        recommendations = [vid for vid, _ in video_scores[:num_recs]]
        
        # Add diversity: force one recommendation from each category
        diversity_vids = {
            cat: [vid for vid in video_pool_dict 
                  if video_pool_dict[vid]['category'] == cat and vid not in recommendations]
            for cat in categories
        }
        
        diversity_picks = []
        for cat in categories:
            if diversity_vids[cat]:
                diversity_picks.append(random.choice(diversity_vids[cat]))
        
        diversity_picks = diversity_picks[:num_recs]
        merged = diversity_picks + [vid for vid in recommendations if vid not in diversity_picks]
        recommendations = injected + [vid for vid in merged if vid not in injected]
        recommendations = recommendations[:num_recs]

    return recommendations[:num_recs]

def run_simulation(user_id, num_sessions):
    """Simulate user interactions over a number of sessions."""
    global users, video_pool_dict
    users = initialize_users(20) if 'users' not in globals() else users
    for session in range(1, num_sessions + 1):
        recs = recommend_videos(user_id, session, CONFIG['initial_recs'])
        for video_id in recs:
            category = video_pool_dict[video_id]['category']
            watch_time = random.randint(CONFIG['min_watch_time'], CONFIG['max_watch_time'])
            liked = random.random() < users[user_id]['category_prefs'].get(category, 0.0) + 0.1
            shared = random.random() < users[user_id]['category_prefs'].get(category, 0.0) * 0.5
            commented = random.random() < users[user_id]['category_prefs'].get(category, 0.0) * 0.2
            users = log_interaction(user_id, video_id, watch_time, liked, shared, commented, session)
    return users

def analyze_user_phase_metrics(user_id):
    """Analyze user engagement metrics across different learning phases."""
    global users
    if user_id not in users:
        return {"error": f"User {user_id} not found"}
    
    phase_data = {'discovery': [], 'personalization': [], 'adaptation': []}
    for interaction in users[user_id]['interactions']:
        session = interaction['session']
        phase = 'discovery' if session <= CONFIG['discovery_end'] else \
                'adaptation' if session > CONFIG['adaptation_start'] else 'personalization'
        engagement = interaction['watch_time']
        if interaction['liked']: engagement += CONFIG['like_bonus']
        if interaction['shared']: engagement += CONFIG['share_bonus']
        if interaction['commented']: engagement += 75  # Comment bonus
        phase_data[phase].append(engagement)
    
    """Calculate the average engagement, For each phase"""
    metrics = {}
    discovery_avg = 0
    personalization_avg = 0
    for phase in phase_data:
        if phase_data[phase]:
            avg_engagement = sum(phase_data[phase]) / len(phase_data[phase])
            metrics[f'{phase}_avg_engagement'] = avg_engagement
            if phase == 'discovery':
                discovery_avg = avg_engagement
            elif phase == 'personalization':
                personalization_avg = avg_engagement
    """
    Measures how engagement changed from discovery → personalization.
    Positive number → user is engaging more over time.
    Negative number → engagement dropped.
    """
    if discovery_avg > 0 and personalization_avg > 0:
        satisfaction_trend = ((personalization_avg - discovery_avg) / discovery_avg) * 100
        metrics['satisfaction_trend'] = satisfaction_trend
    metrics['pref_shifts'] = users[user_id]['category_prefs'].copy()
    return metrics

def analyze_video_performance():
    global video_pool_dict
    video_metrics = {}
    total_interactions = sum(len(users[user_id]['interactions']) for user_id in users)
    for video_id, video in video_pool_dict.items():
        perf = video['performance']
        if perf['total_engages'] > 0:
            completion_velocity = perf['total_engages'] / total_interactions
            video_metrics[video_id] = {
                'avg_completion': perf['avg_completion'],
                'completion_velocity': completion_velocity,
                'total_engages': perf['total_engages'],
                'is_viral': perf['avg_completion'] > CONFIG['viral_threshold'] and perf['total_engages'] > sum(v['performance']['total_engages'] for v in video_pool_dict.values()) / len(video_pool_dict)
            }
    top_virals = sorted(video_metrics.items(), key=lambda x: x[1]['completion_velocity'], reverse=True)[:3]
    category_dominance = {cat: 0 for cat in categories}
    total_engages = sum(v['performance']['total_engages'] for v in video_pool_dict.values())
    for cat in categories:
        cat_videos = [v for v in video_pool_dict if video_pool_dict[v]['category'] == cat]
        if cat_videos:
            cat_engages = sum(video_pool_dict[v]['performance']['total_engages'] for v in cat_videos)
            category_dominance[cat] = cat_engages / total_engages if total_engages > 0 else 0
    return {'video_metrics': video_metrics, 'top_virals': top_virals, 'category_dominance': category_dominance}

def measure_algo_effectiveness():
    global users
    effectiveness = {}
    for user_id in users:
        interactions = users[user_id]['interactions']
        if not interactions:
            continue
        high_engagement_recs = sum(1 for i in interactions if i['completion'] > 0.5) / len(interactions)
        effectiveness[user_id] = {'rec_accuracy': high_engagement_recs * 100}

        """Track engagement by phase"""

        phase_engagements = {'discovery': [], 'personalization': [], 'adaptation': []}
        for i in interactions:
            phase = 'discovery' if i['session'] <= CONFIG['discovery_end'] else \
                    'adaptation' if i['session'] > CONFIG['adaptation_start'] else 'personalization'
            engagement = i['watch_time']
            if i['liked']: engagement += CONFIG['like_bonus']
            if i['shared']: engagement += CONFIG['share_bonus']
            if i['commented']: engagement += 75
            phase_engagements[phase].append(engagement)

            """Measure personalization boost"""

        if phase_engagements['discovery'] and phase_engagements['personalization']:
            personalization_boost = ((sum(phase_engagements['personalization']) / len(phase_engagements['personalization']) if phase_engagements['personalization'] else 0) - 
                                  (sum(phase_engagements['discovery']) / len(phase_engagements['discovery']))) / (sum(phase_engagements['discovery']) / len(phase_engagements['discovery'])) * 100
            effectiveness[user_id]['personalization_boost'] = personalization_boost
            """
            Measure diversity balance:
                Counts how many unique categories the user actually interacted with.
                Divides by total number of categories → percentage coverage.
                Measures whether the algorithm shows a balanced mix of content, not just one category.
            """
        unique_cats = set(video_pool_dict[i['video_id']]['category'] for i in interactions)
        diversity_balance = len(unique_cats) / len(categories) if categories else 0
        effectiveness[user_id]['diversity_balance'] = diversity_balance * 100
    return effectiveness

def generate_insights():
    """
    takes all the user and video data, pulls out key metrics from your simulation, and turns them into a readable summary:
        How users engagement changes across phases
        Which videos went viral and why
        Overall algorithm recommendation accuracy
    """
    global users
    insights = []
    for user_id in users:
        metrics = analyze_user_phase_metrics(user_id)
        if 'error' not in metrics:
            discovery_avg = metrics.get('discovery_avg_engagement', 0)
            personalization_avg = metrics.get('personalization_avg_engagement', 0)
            trend = metrics.get('satisfaction_trend', 0)
            insights.append(f"{user_id} engagement: Discovery avg {discovery_avg:.1f}s → Personalization {personalization_avg:.1f}s ({trend:+.1f}%)")
    video_data = analyze_video_performance()
    total_interactions = sum(len(users[user_id]['interactions']) for user_id in users)  # Define here
    for vid, data in video_data['top_virals']:
        insights.append(f"Top viral: Video {vid} ({video_pool_dict[vid]['title']}) - {data['avg_completion']*100:.1f}% completion, boosted recs {data['total_engages']*100/total_interactions:.1f}%")
    algo_data = measure_algo_effectiveness()
    avg_accuracy = sum(d['rec_accuracy'] for d in algo_data.values()) / len(algo_data) if algo_data else 0
    insights.append(f"Algo accuracy: {avg_accuracy:.1f}% across users")
    return insights

def plot_user_engagement(user_id):
    metrics = analyze_user_phase_metrics(user_id)
    phases = ['discovery', 'personalization', 'adaptation']
    labels = ['Discovery', 'Personalization', 'Adaptation']
    phase_colors = ['#5B8DB8', '#F5C842', '#6DB56D']
    engagements = [metrics.get(f'{p}_avg_engagement', 0) for p in phases]
    trend = metrics.get('satisfaction_trend', 0)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, engagements, color=phase_colors, width=0.5, edgecolor='white', linewidth=1.2)

    for bar, val in zip(bars, engagements):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                f'{val:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    trend_color = '#2ECC71' if trend >= 0 else '#E74C3C'
    trend_symbol = '▲' if trend >= 0 else '▼'
    ax.annotate(f'Discovery → Personalization\n{trend_symbol} {abs(trend):.1f}% change',
                xy=(0.98, 0.95), xycoords='axes fraction', ha='right', va='top',
                fontsize=10, color=trend_color,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=trend_color, alpha=0.8))

    ax.set_title(f'{user_id} — Avg Engagement Score by Phase', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel('Avg Engagement Score\n(watch time + action bonuses)', fontsize=10)
    ax.set_ylim(0, max(engagements) * 1.25 if any(engagements) else 10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(f'{user_id}_engagement.png', dpi=120)
    plt.close()

def plot_top_videos():
    video_data = analyze_video_performance()
    top_vids = video_data['top_virals']
    vids, data = zip(*top_vids)
    titles = [video_pool_dict[v]['title'] for v in vids]
    cats = [video_pool_dict[v]['category'] for v in vids]
    completions = [d['avg_completion'] * 100 for d in data]
    engages = [d['total_engages'] for d in data]
    colors = [CATEGORY_COLORS.get(cat, '#888888') for cat in cats]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(titles, completions, color=colors, width=0.5, edgecolor='white', linewidth=1.2)

    for bar, val, eng, cat in zip(bars, completions, engages, cats):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'{val:.1f}%\n({eng} engages)', ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.text(bar.get_x() + bar.get_width() / 2, -2.5,
                cat, ha='center', va='top', fontsize=9,
                color=CATEGORY_COLORS.get(cat, '#888888'), fontstyle='italic')

    ax.set_title('Top 3 Viral Videos — Completion Rate & Total Engagements', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel('Avg Completion Rate (%)', fontsize=10)
    ax.set_ylim(0, max(completions) * 1.35 if any(completions) else 10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig('top_videos.png', dpi=120)
    plt.close()

def plot_category_dominance():
    video_data = analyze_video_performance()
    dominance = video_data['category_dominance']
    cats = list(dominance.keys())
    values = [dominance[c] * 100 for c in cats]
    colors = [CATEGORY_COLORS.get(c, '#888888') for c in cats]
    equal_share = 100 / len(cats)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(cats, values, color=colors, width=0.5, edgecolor='white', linewidth=1.2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.axhline(equal_share, color='#E74C3C', linestyle='--', linewidth=1.4,
               label=f'Equal share ({equal_share:.0f}%)')
    ax.legend(fontsize=10)

    ax.set_title('Category Engagement Dominance Across All Users', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel('Share of Total Engagements (%)', fontsize=10)
    ax.set_ylim(0, max(values) * 1.3 if any(values) else 10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig('category_dominance.png', dpi=120)
    plt.close()

if __name__ == "__main__":
    """ 
    Creates videos and users
    Runs the simulation for all users
    Prints key results for inspection
    Generates textual insights
    Creates visualizations
    
    """
    video_pool_dict = video_pool()
    users = initialize_users(20)
    print("Initial users:", users)
    
    # Run simulation for all 20 users with 50 sessions
    for user_id in users:
        users = run_simulation(user_id, 50)
    print("After simulation - All users:", {k: {'interactions': len(v['interactions']), 'phase': v['phase']} for k, v in users.items()})
    print("Video 1 performance:", video_pool_dict[1])
    print("Top ranked videos:", get_video_rank()[:5])
    print("Recommendations for User1 (session 25):", recommend_videos('User1', 25, 6))
    
    # Add analytics
    insights = generate_insights()
    for insight in insights:
        print(insight)
    
    # Add visualizations
    for user_id in users:
        plot_user_engagement(user_id)
    plot_top_videos()
    plot_category_dominance()
