from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import yfinance as yf
import datetime
from datetime import datetime
import requests
import feedparser
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MongoDB connection
# client = MongoClient("mongodb+srv://admin:admin@cluster0.tgpyua2.mongodb.net/")  # MongoDB Atlas
client = MongoClient("mongodb://localhost:27017/")  # MongoDB
db = client['stock_app']  # Database name
users_collection = db['users']  # Collection name

@app.route('/home')
def home_dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['user'] = username
            return redirect('/home')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=None)


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if users_collection.find_one({'username': username}):
        return render_template('login.html', error='Username already exists!')

    users_collection.insert_one({
        'username': username,
        'email': email,
        'password': password,
        'watchlist': []
    })
    session['user'] = username
    return redirect('/home')

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def watchlist():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = users_collection.find_one({'username': session['user']})

    if request.method == 'GET':
        return jsonify(user.get('watchlist', []))

    data = request.json
    symbol = data.get('symbol')

    if request.method == 'POST':
        if symbol not in user.get('watchlist', []):
            users_collection.update_one(
                {'username': session['user']},
                {'$push': {'watchlist': symbol}}
            )
        return jsonify({'status': 'added'})

    if request.method == 'DELETE':
        users_collection.update_one(
            {'username': session['user']},
            {'$pull': {'watchlist': symbol}}
        )
        return jsonify({'status': 'removed'})

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/api/search')
def search_stocks():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])

    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify([])

    results = response.json().get('quotes', [])
    suggestions = []
    for r in results:
        if 'symbol' in r and 'shortname' in r:
            suggestions.append({
                'symbol': r['symbol'],
                'name': r['shortname']
            })
    return jsonify(suggestions[:8])  # return top 8 suggestions

@app.route('/api/data')
def api_data():
    symbol = request.args.get('symbol', 'TCS.NS').upper()
    period = request.args.get('period', '1mo')  # default 1 month
    tk = yf.Ticker(symbol)
    hist = tk.history(period=period, interval='1h' if period in ['1d', '5d'] else '1d')

    # If empty data, try adding .NS suffix
    if hist.empty and not symbol.endswith('.NS'):
        tk = yf.Ticker(symbol + '.NS')
        hist = tk.history(period=period, interval='1h' if period in ['1d', '5d'] else '1d')

    prices = hist['Close'].tolist()
    timestamps = [ts.strftime('%Y-%m-%d %H:%M' if period in ['1d', '5d'] else '%Y-%m-%d') for ts in hist.index]
    high = max(prices) if prices else None
    low = min(prices) if prices else None
    info = tk.info
    about = info.get('longBusinessSummary', '')
    data = {
        'symbol': symbol,
        'name': info.get('shortName', symbol),
        'price': prices[-1] if prices else 'N/A',
        'prices': prices,
        'timestamps': timestamps,
        'high': high,
        'low': low,
        'about': about[:225] + '...' if len(about) > 225 else about,
        'sector': info.get('sector', 'N/A'),
        'industry': info.get('industry', 'N/A'),
        'website': info.get('website', 'N/A'),
        # 'previousClose': info.get('previousClose', 'N/A'),
        # 'currency': info.get('currency', 'INR'),
        # 'marketCap': info.get('marketCap', 'N/A'),
        # 'trailingPE': info.get('trailingPE', 'N/A'),
        # 'dividendYield': (
        #     f"{round(info['dividendYield'] * 100, 2)}%" if info.get('dividendYield') else 'N/A'
        # ),
        # 'dividendRate': info.get('dividendRate', 'N/A'),
        # 'quoteType': info.get('quoteType', 'N/A')
        # 'logo_url': info.get('logo_url', ''),
    }
    # Optional: For ETFs or Funds, modify how sector/industry appears
    if info.get('quoteType') in ['ETF', 'MUTUALFUND']:
        data['sector'] = 'Exchange-Traded Fund'
        data['industry'] = info.get('category', 'N/A')

    return jsonify(data)

@app.route('/news')
def news():
    import feedparser
    from bs4 import BeautifulSoup
    from datetime import datetime

    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    news_items = []

    for entry in feed.entries[:50]:
        # Try to get image from <media:content> or <enclosure>
        image_url = None
        if "media_content" in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0].get("url")
        elif "links" in entry:
            for link in entry.links:
                if link.get("type", "").startswith("image/"):
                    image_url = link.get("href")
                    break

        # Fallback to scraping from summary HTML
        if not image_url:
            soup = BeautifulSoup(entry.get("summary", ""), "html.parser")
            img_tag = soup.find("img")
            image_url = img_tag["src"] if img_tag else "/static/default-img.png"

        # Extract text content
        soup = BeautifulSoup(entry.get("summary", ""), "html.parser")
        text = soup.get_text().strip()

        news_items.append({
            'title': entry.get("title"),
            'link': entry.get("link"),
            'description': text[:300] + "..." if len(text) > 300 else text,
            'publishedAt': entry.get("published", ""),
            'source': entry.get("source", {}).get("title", "Google News"),
            'image_url': image_url
        })

    now = datetime.now()
    return render_template("news.html", news=news_items, now=now)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def home():
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
