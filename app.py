from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import yfinance as yf
import datetime
from datetime import datetime
import requests
import feedparser
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/home')
def home_dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username']=='saketh' and request.form['password']=='12345':
            session['user'] = 'saketh'
            return redirect('/home')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=None)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/api/data')
def api_data():
    symbol = request.args.get('symbol', 'TCS.NS')
    period = request.args.get('period', '1mo')  # default 1 month
    tk = yf.Ticker(symbol)
    hist = tk.history(period=period, interval='1h' if period in ['1d', '5d'] else '1d')
    prices = hist['Close'].tolist()
    timestamps = [ts.strftime('%Y-%m-%d %H:%M' if period in ['1d', '5d'] else '%Y-%m-%d') for ts in hist.index]
    high = max(prices) if prices else None
    low = min(prices) if prices else None
    info = tk.info
    about = info.get('longBusinessSummary', '')
    return jsonify({
        'symbol': symbol,
        'name': info.get('shortName', symbol),
        'price': prices[-1] if prices else 'N/A',
        'prices': prices,
        'timestamps': timestamps,
        'high': high,
        'low': low,
        'about': about[:225] + '...' if len(about) > 225 else about,
        'sector': info.get('sector', ''),
        'industry': info.get('industry', ''),
        'website': info.get('website', ''),
        # 'logo_url': info.get('logo_url', ''),
    })

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
