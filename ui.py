import streamlit as st
import requests
import time
from datetime import datetime, timedelta, timezone

# Page configuration
st.set_page_config(
    page_title="GitHub Actions Monitor",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force dark theme with black background
st.markdown("""
    <style>
    /* Force black background */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
    }
    [data-testid="stHeader"] {
        background-color: #000000;
    }
    .main {
        background-color: #000000;
    }
    /* Make all text white by default */
    .main * {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:5000/webhook/events"

def format_timestamp(timestamp_str):
    """Format ISO timestamp to readable format, converting UTC to IST"""
    try:
        # Parse the timestamp (assuming it's in UTC)
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # If timestamp is naive (no timezone), assume it's UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # Convert to IST (UTC+5:30)
        IST = timezone(timedelta(hours=5, minutes=30))
        dt_ist = dt.astimezone(IST)
        
        return dt_ist.strftime("%d %B %Y - %I:%M %p IST")
    except:
        return timestamp_str

def format_event_message(event):
    """Format event data into readable message"""
    author = event.get('author', 'Unknown')
    action = event.get('action', '')
    from_branch = event.get('from_branch', '')
    to_branch = event.get('to_branch', '')
    timestamp = format_timestamp(event.get('timestamp', ''))
    
    if action == 'PUSH':
        return f'**{author}** pushed to **{to_branch}** on {timestamp}'
    elif action == 'PULL_REQUEST':
        return f'**{author}** submitted a pull request from **{from_branch}** to **{to_branch}** on {timestamp}'
    elif action == 'MERGE':
        return f'**{author}** merged branch **{from_branch}** to **{to_branch}** on {timestamp}'
    else:
        return f'Unknown action by {author}'

def get_action_icon(action):
    """Get icon based on action type"""
    icons = {
        'PUSH': '🚀',
        'PULL_REQUEST': '🔀',
        'MERGE': '✅'
    }
    return icons.get(action, '📌')

def get_action_color(action):
    """Get color based on action type"""
    colors = {
        'PUSH': '#3b82f6',  # blue
        'PULL_REQUEST': '#f59e0b',  # orange
        'MERGE': '#10b981'  # green
    }
    return colors.get(action, '#6b7280')

def fetch_events():
    """Fetch events from the Flask API"""
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('events', [])
        else:
            st.error(f"Failed to fetch events: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to the webhook server. Please ensure the Flask app is running on port 5000.")
        return []
    except Exception as e:
        st.error(f"Error fetching events: {str(e)}")
        return []

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #d1d5db;
        margin-bottom: 2rem;
    }
    .event-card {
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid;
        background-color: #1f2937;
        box-shadow: 0 1px 3px rgba(255,255,255,0.1);
    }
    .event-header {
        display: flex;
        align-items: center;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .event-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .no-events {
        text-align: center;
        padding: 3rem;
        color: #9ca3af;
        font-size: 1.2rem;
        background-color: #000000;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stats-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔔 GitHub Actions Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-time monitoring of GitHub repository events</div>', unsafe_allow_html=True)

# Create columns for stats and refresh button
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

# Placeholder for auto-refresh
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Fetch events
events = fetch_events()

# Display statistics
with col1:
    st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
            <div class="stats-number">{len(events)}</div>
            <div class="stats-label">Total Events</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    push_count = sum(1 for e in events if e.get('action') == 'PUSH')
    st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);">
            <div class="stats-number">{push_count}</div>
            <div class="stats-label">Pushes</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    pr_count = sum(1 for e in events if e.get('action') == 'PULL_REQUEST')
    merge_count = sum(1 for e in events if e.get('action') == 'MERGE')
    st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
            <div class="stats-number">{pr_count}</div>
            <div class="stats-label">Pull Requests</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    # Auto-refresh indicator
    time_since_refresh = int(time.time() - st.session_state.last_refresh)
    st.caption(f"Last refreshed: {time_since_refresh}s ago")

st.markdown("---")

# Display events
if events:
    st.subheader(f"📋 Recent Activity ({len(events)} events)")
    
    for event in events:
        action = event.get('action', '')
        color = get_action_color(action)
        icon = get_action_icon(action)
        message = format_event_message(event)
        
        st.markdown(f"""
            <div class="event-card" style="border-left-color: {color};">
                <div class="event-header">
                    <span class="event-icon">{icon}</span>
                    <span>{message}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="no-events">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📭</div>
            <div>No events yet</div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem;">
                Waiting for GitHub webhook events...
            </div>
        </div>
    """, unsafe_allow_html=True)

# Auto-refresh every 15 seconds
st.markdown("---")
st.caption("🔄 Auto-refreshing every 15 seconds...")

# JavaScript for auto-refresh
st.markdown("""
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 15000);
    </script>
""", unsafe_allow_html=True)

# Update last refresh time
st.session_state.last_refresh = time.time()