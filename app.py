import os
import json
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, 'accounts')
os.makedirs(ACCOUNTS_DIR, exist_ok=True)

HTML_ADMIN = '''
<!DOCTYPE html>
<html>
<head>
    <title>TikTok Auto-Pilot Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-2 text-indigo-400">TikTok Auto-Pilot Engine</h1>
        <p class="text-gray-400 mb-6">Manage multi-account video queues & posting schedules.</p>
        
        <!-- Add New Account -->
        <div class="bg-gray-800 p-6 rounded-lg mb-8 shadow-md border border-gray-700">
            <h2 class="text-xl font-semibold mb-4 text-yellow-400">Create New Account Workspace</h2>
            <form action="/add_account" method="POST" class="flex gap-4">
                <input type="text" name="acc_name" placeholder="Account Name (e.g., brand_account_1)" class="bg-gray-700 px-4 py-2 rounded flex-1 text-white border border-gray-600 focus:outline-none focus:border-indigo-500" required>
                <button type="submit" class="bg-indigo-600 px-6 py-2 rounded font-bold hover:bg-indigo-500 transition">Create Account</button>
            </form>
        </div>

        <!-- Account List & Configuration -->
        <h2 class="text-2xl font-bold mb-4">Active Accounts</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {% if accounts %}
                {% for acc in accounts %}
                <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-md">
                    <div class="flex justify-between items-center mb-3">
                        <h3 class="text-xl font-bold text-green-400">{{ acc.name }}</h3>
                        <span class="bg-gray-700 text-xs px-2 py-1 rounded text-gray-300">Pending: {{ acc.pending_count }}</span>
                    </div>
                    <p class="text-xs text-gray-400 mb-4">Videos folder: <code>accounts/{{ acc.name }}/raw_videos/</code></p>
                    
                    <form action="/update_config" method="POST" class="space-y-3">
                        <input type="hidden" name="acc_name" value="{{ acc.name }}">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="text-xs text-gray-400">Min Gap (Hours):</label>
                                <input type="number" step="0.1" name="min_hours" value="{{ acc.config.min_hours }}" class="w-full bg-gray-700 px-3 py-1 rounded text-sm border border-gray-600">
                            </div>
                            <div>
                                <label class="text-xs text-gray-400">Max Gap (Hours):</label>
                                <input type="number" step="0.1" name="max_hours" value="{{ acc.config.max_hours }}" class="w-full bg-gray-700 px-3 py-1 rounded text-sm border border-gray-600">
                            </div>
                        </div>
                        <button type="submit" class="w-full bg-emerald-600 py-2 rounded font-bold hover:bg-emerald-500 transition text-sm">Save Config</button>
                    </form>
                </div>
                {% endfor %}
            {% else %}
                <div class="col-span-2 text-gray-500 bg-gray-800 p-6 rounded-lg text-center">
                    No accounts created yet. Create one above to start!
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    accounts_data = []
    if os.path.exists(ACCOUNTS_DIR):
        for acc in os.listdir(ACCOUNTS_DIR):
            acc_path = os.path.join(ACCOUNTS_DIR, acc)
            if not os.path.isdir(acc_path):
                continue
            raw_path = os.path.join(acc_path, 'raw_videos')
            config_file = os.path.join(acc_path, 'config.json')
            
            pending = len([f for f in os.listdir(raw_path) if f.lower().endswith(('.mp4', '.mov', '.webm'))]) if os.path.exists(raw_path) else 0
            config = {"min_hours": 4, "max_hours": 8}
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config.update(json.load(f))
                except:
                    pass
                    
            accounts_data.append({"name": acc, "pending_count": pending, "config": config})
            
    return render_template_string(HTML_ADMIN, accounts=accounts_data)

@app.route('/add_account', methods=['POST'])
def add_account():
    name = request.form.get('acc_name', '').strip()
    if name:
        acc_path = os.path.join(ACCOUNTS_DIR, name)
        os.makedirs(os.path.join(acc_path, 'raw_videos'), exist_ok=True)
        os.makedirs(os.path.join(acc_path, 'uploaded'), exist_ok=True)
        config_file = os.path.join(acc_path, 'config.json')
        if not os.path.exists(config_file):
            with open(config_file, 'w') as f:
                json.dump({"min_hours": 4, "max_hours": 8, "daily_limit": 5}, f, indent=4)
    return redirect(url_for('index'))

@app.route('/update_config', methods=['POST'])
def update_config():
    name = request.form.get('acc_name')
    min_h = float(request.form.get('min_hours', 4))
    max_h = float(request.form.get('max_hours', 8))
    
    acc_path = os.path.join(ACCOUNTS_DIR, name)
    config_file = os.path.join(acc_path, 'config.json')
    
    config = {"min_hours": min_h, "max_hours": max_h, "daily_limit": 5}
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)