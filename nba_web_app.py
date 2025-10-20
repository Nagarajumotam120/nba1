# nba_web_app.py
from flask import Flask, render_template_string, request, jsonify
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Sample NBA Data
def init_sample_data():
    conn = sqlite3.connect('nba_sample.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            conference TEXT,
            wins INTEGER,
            losses INTEGER,
            ppg REAL,
            opp_ppg REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            team TEXT,
            position TEXT,
            ppg REAL,
            rpg REAL,
            apg REAL,
            fg_pct REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            date TEXT,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER
        )
    ''')
    
    # Sample teams data
    teams = [
        (1, 'Los Angeles Lakers', 'West', 42, 30, 115.6, 112.3),
        (2, 'Golden State Warriors', 'West', 38, 34, 118.3, 115.8),
        (3, 'Boston Celtics', 'East', 57, 15, 121.1, 109.8),
        (4, 'Chicago Bulls', 'East', 34, 38, 111.8, 113.5),
        (5, 'Miami Heat', 'East', 40, 32, 113.4, 111.2),
        (6, 'Denver Nuggets', 'West', 52, 20, 117.5, 112.9),
        (7, 'Phoenix Suns', 'West', 44, 28, 116.8, 113.1),
        (8, 'Milwaukee Bucks', 'East', 48, 24, 119.3, 114.6)
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO teams VALUES (?, ?, ?, ?, ?, ?, ?)', teams)
    
    # Sample players data
    players = [
        (1, 'LeBron James', 'Los Angeles Lakers', 'SF', 25.3, 7.3, 8.3, 53.5),
        (2, 'Stephen Curry', 'Golden State Warriors', 'PG', 27.5, 4.3, 5.2, 45.3),
        (3, 'Giannis Antetokounmpo', 'Milwaukee Bucks', 'PF', 30.8, 11.5, 6.4, 61.3),
        (4, 'Kevin Durant', 'Phoenix Suns', 'SF', 27.6, 6.8, 5.2, 52.9),
        (5, 'Luka Dončić', 'Dallas Mavericks', 'PG', 34.1, 9.0, 9.8, 49.2),
        (6, 'Jayson Tatum', 'Boston Celtics', 'SF', 27.2, 8.3, 4.9, 47.1),
        (7, 'Nikola Jokić', 'Denver Nuggets', 'C', 26.4, 12.4, 9.0, 58.3),
        (8, 'Joel Embiid', 'Philadelphia 76ers', 'C', 35.3, 11.3, 5.7, 53.7)
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO players VALUES (?, ?, ?, ?, ?, ?, ?, ?)', players)
    
    conn.commit()
    conn.close()

def create_win_loss_chart():
    """Create a matplotlib chart for team wins/losses"""
    conn = sqlite3.connect('nba_sample.db')
    df = pd.read_sql_query("SELECT name, wins, losses FROM teams ORDER BY wins DESC", conn)
    conn.close()
    
    plt.figure(figsize=(10, 6))
    x = np.arange(len(df))
    width = 0.35
    
    plt.bar(x - width/2, df['wins'], width, label='Wins', color='#1d428a')
    plt.bar(x + width/2, df['losses'], width, label='Losses', color='#c8102e')
    
    plt.xlabel('Teams')
    plt.ylabel('Games')
    plt.title('NBA Team Wins vs Losses')
    plt.xticks(x, df['name'], rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    # Save to bytes
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def create_points_chart():
    """Create a points per game chart"""
    conn = sqlite3.connect('nba_sample.db')
    df = pd.read_sql_query("SELECT name, ppg FROM teams ORDER BY ppg DESC", conn)
    conn.close()
    
    plt.figure(figsize=(10, 6))
    colors = ['#1d428a' if x == df['ppg'].max() else '#c8102e' if x == df['ppg'].min() else '#2c5aa0' for x in df['ppg']]
    
    plt.bar(df['name'], df['ppg'], color=colors)
    plt.xlabel('Teams')
    plt.ylabel('Points Per Game')
    plt.title('NBA Team Points Per Game')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBA Data Hub</title>
    <style>
        :root {
            --primary: #1d428a;
            --secondary: #c8102e;
            --dark: #0c1b33;
            --light: #f8f9fa;
            --gray: #6c757d;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
        }
        
        /* Header */
        header {
            background: linear-gradient(135deg, var(--primary), var(--dark));
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo i {
            font-size: 2rem;
            color: var(--secondary);
        }
        
        .logo h1 {
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        nav ul {
            display: flex;
            list-style: none;
        }
        
        nav ul li {
            margin-left: 1.5rem;
        }
        
        nav ul li a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            padding: 0.5rem 0;
        }
        
        nav ul li a:hover {
            color: var(--secondary);
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(rgba(13, 29, 56, 0.8), rgba(13, 29, 56, 0.9));
            background-size: cover;
            color: white;
            padding: 3rem 0;
            text-align: center;
        }
        
        .hero h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .hero p {
            font-size: 1.2rem;
            max-width: 700px;
            margin: 0 auto 2rem;
        }
        
        .btn {
            display: inline-block;
            background-color: var(--secondary);
            color: white;
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
        }
        
        .btn:hover {
            background-color: #a00d24;
            transform: translateY(-2px);
        }
        
        /* Main Content */
        .main-content {
            padding: 3rem 0;
        }
        
        .section-title {
            text-align: center;
            margin-bottom: 2rem;
            color: var(--primary);
            position: relative;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 4px;
            background-color: var(--secondary);
        }
        
        /* Dashboard */
        .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .stat-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card i {
            font-size: 2rem;
            color: var(--primary);
            margin-bottom: 1rem;
        }
        
        .stat-card h3 {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
            color: var(--dark);
        }
        
        .stat-card p {
            color: var(--gray);
            font-weight: 500;
        }
        
        /* Charts */
        .charts-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .chart-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .chart-container img {
            width: 100%;
            height: auto;
        }
        
        /* Tables */
        .data-table {
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 3rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        thead {
            background-color: var(--primary);
            color: white;
        }
        
        th, td {
            padding: 1rem;
            text-align: left;
        }
        
        tbody tr {
            border-bottom: 1px solid #eee;
        }
        
        tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        /* Footer */
        footer {
            background-color: var(--dark);
            color: white;
            padding: 2rem 0;
            text-align: center;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .copyright {
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #aaa;
        }
        
        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }
            
            nav ul {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            nav ul li {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-basketball-ball"></i>
                    <h1>NBA Data Hub</h1>
                </div>
                <nav>
                    <ul>
                        <li><a href="#dashboard">Dashboard</a></li>
                        <li><a href="#teams">Teams</a></li>
                        <li><a href="#players">Players</a></li>
                        <li><a href="#visualizations">Visualizations</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h2>NBA Data Management & Visualization</h2>
            <p>Explore comprehensive NBA statistics, team performance, player analytics, and interactive visualizations</p>
            <a href="#dashboard" class="btn">Explore Data</a>
        </div>
    </section>

    <!-- Main Content -->
    <main class="main-content">
        <div class="container">
            <!-- Dashboard Section -->
            <section id="dashboard">
                <h2 class="section-title">NBA Dashboard</h2>
                
                <div class="dashboard-stats">
                    <div class="stat-card">
                        <i class="fas fa-basketball-ball"></i>
                        <h3>{{ total_teams }}</h3>
                        <p>NBA Teams</p>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-users"></i>
                        <h3>{{ total_players }}</h3>
                        <p>Featured Players</p>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-trophy"></i>
                        <h3>{{ avg_ppg }}</h3>
                        <p>Average PPG</p>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-chart-line"></i>
                        <h3>{{ best_team }}</h3>
                        <p>Best Record</p>
                    </div>
                </div>
            </section>

            <!-- Visualizations Section -->
            <section id="visualizations">
                <h2 class="section-title">Data Visualizations</h2>
                
                <div class="charts-grid">
                    <div class="chart-container">
                        <h3>Team Wins vs Losses</h3>
                        <img src="data:image/png;base64,{{ win_loss_chart }}" alt="Wins vs Losses Chart">
                    </div>
                    <div class="chart-container">
                        <h3>Points Per Game</h3>
                        <img src="data:image/png;base64,{{ points_chart }}" alt="Points Per Game Chart">
                    </div>
                </div>
            </section>

            <!-- Teams Section -->
            <section id="teams">
                <h2 class="section-title">NBA Teams</h2>
                
                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Team</th>
                                <th>Conference</th>
                                <th>W-L Record</th>
                                <th>Win %</th>
                                <th>PPG</th>
                                <th>Opp PPG</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for team in teams %}
                            <tr>
                                <td><strong>{{ team.name }}</strong></td>
                                <td>{{ team.conference }}</td>
                                <td>{{ team.wins }}-{{ team.losses }}</td>
                                <td>{{ "%.3f"|format(team.wins/(team.wins+team.losses)) }}</td>
                                <td>{{ team.ppg }}</td>
                                <td>{{ team.opp_ppg }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Players Section -->
            <section id="players">
                <h2 class="section-title">Top Players</h2>
                
                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Player</th>
                                <th>Team</th>
                                <th>Position</th>
                                <th>PPG</th>
                                <th>RPG</th>
                                <th>APG</th>
                                <th>FG%</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for player in players %}
                            <tr>
                                <td><strong>{{ player.name }}</strong></td>
                                <td>{{ player.team }}</td>
                                <td>{{ player.position }}</td>
                                <td>{{ player.ppg }}</td>
                                <td>{{ player.rpg }}</td>
                                <td>{{ player.apg }}</td>
                                <td>{{ "%.1f"|format(player.fg_pct) }}%</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    </main>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div>
                    <h3>NBA Data Hub</h3>
                    <p>Your premier destination for comprehensive NBA statistics and analytics.</p>
                </div>
                <div>
                    <h3>Quick Links</h3>
                    <p><a href="#dashboard" style="color: #ccc;">Dashboard</a></p>
                    <p><a href="#teams" style="color: #ccc;">Teams</a></p>
                    <p><a href="#players" style="color: #ccc;">Players</a></p>
                </div>
            </div>
            <div class="copyright">
                <p>&copy; 2023 NBA Data Hub. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    # Initialize sample data
    init_sample_data()
    
    # Connect to database
    conn = sqlite3.connect('nba_sample.db')
    
    # Get teams data
    teams = pd.read_sql_query("SELECT * FROM teams ORDER BY wins DESC", conn).to_dict('records')
    
    # Get players data
    players = pd.read_sql_query("SELECT * FROM players ORDER BY ppg DESC", conn).to_dict('records')
    
    # Calculate stats for dashboard
    total_teams = len(teams)
    total_players = len(players)
    avg_ppg = round(pd.read_sql_query("SELECT AVG(ppg) as avg_ppg FROM teams", conn)['avg_ppg'].iloc[0], 1)
    
    # Find team with best record
    best_team_df = pd.read_sql_query("SELECT name, wins, losses FROM teams ORDER BY wins DESC LIMIT 1", conn)
    best_team = f"{best_team_df['name'].iloc[0]} ({best_team_df['wins'].iloc[0]}-{best_team_df['losses'].iloc[0]})"
    
    conn.close()
    
    # Create charts
    win_loss_chart = create_win_loss_chart()
    points_chart = create_points_chart()
    
    return render_template_string(HTML_TEMPLATE, 
                                teams=teams,
                                players=players,
                                total_teams=total_teams,
                                total_players=total_players,
                                avg_ppg=avg_ppg,
                                best_team=best_team,
                                win_loss_chart=win_loss_chart,
                                points_chart=points_chart)

@app.route('/api/teams')
def api_teams():
    conn = sqlite3.connect('nba_sample.db')
    teams = pd.read_sql_query("SELECT * FROM teams", conn).to_dict('records')
    conn.close()
    return jsonify(teams)

@app.route('/api/players')
def api_players():
    conn = sqlite3.connect('nba_sample.db')
    players = pd.read_sql_query("SELECT * FROM players", conn).to_dict('records')
    conn.close()
    return jsonify(players)

if __name__ == '__main__':
    print("🚀 Starting NBA Data Hub...")
    print("📊 Initializing sample data...")
    init_sample_data()
    print("🌐 Web server starting at http://localhost:5000")
    print("✅ NBA Data Hub is ready!")
    app.run(debug=True, host='0.0.0.0', port=5000)