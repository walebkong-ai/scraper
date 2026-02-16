# KW AI News Dashboard 🚀

A beautiful, premium news aggregator dashboard that curates content from **AI, Crypto, and Consulting** sources - all in one elegant interface.

![Dashboard Preview](dashboard/preview.png)

## ✨ Features

### Multi-Vertical News Coverage
- **🤖 AI News**: Ben's Bites, AI Rundown
- **🪙 Crypto News**: CoinTelegraph, Decrypt
- **💼 Consulting**: McKinsey Insights, Harvard Business Review

### Premium UI/UX
- 🎨 **KW Brand Design**: Black & gold color scheme with purple gradients
- 🏷️ **Category Filtering**: Filter by AI, Crypto, or Consulting
- 🔍 **Smart Search**: Search across all sources
- 💾 **Save Articles**: Persistent saved articles with localStorage
- 📱 **Responsive Design**: Works beautifully on all devices
- ⚡ **Smooth Animations**: Premium micro-interactions

### Robust Architecture
- **RSS-Based Scrapers**: Reliable, deterministic data extraction
- **24-Hour Filtering**: Fresh content from the last 24-72 hours
- **Error Handling**: Graceful failure with detailed logging
- **Schema Validation**: Consistent data structure across all sources

## 🚀 Quick Start

### Prerequisites
```bash
python3 --version  # Python 3.8+
pip3 --version
```

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Scraperrrr
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Run scrapers**
```bash
# AI News
python3 tools/scrape_bens_bites.py
python3 tools/scrape_ai_rundown.py

# Crypto News
python3 tools/scrape_cointelegraph.py
python3 tools/scrape_decrypt.py

# Consulting (Note: May have RSS feed issues)
python3 tools/scrape_mckinsey.py
python3 tools/scrape_hbr.py
```

4. **Open the dashboard**
```bash
open dashboard/index.html
# Or navigate to: file:///<path-to-project>/dashboard/index.html
```

## 📁 Project Structure

```
Scraperrrr/
├── dashboard/              # Front-end dashboard
│   ├── index.html         # Main HTML
│   ├── styles.css         # Premium styling
│   └── app.js             # Interactive functionality
├── tools/                 # Python scrapers
│   ├── scrape_bens_bites.py
│   ├── scrape_ai_rundown.py
│   ├── scrape_cointelegraph.py
│   ├── scrape_decrypt.py
│   ├── scrape_mckinsey.py
│   └── scrape_hbr.py
├── architecture/          # Architecture SOPs
│   ├── scraper_bens_bites.md
│   └── scraper_ai_rundown.md
├── .tmp/                  # Temporary files & logs
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎯 Scraper Status

| Source | Status | Articles (24h) | Notes |
|--------|--------|----------------|-------|
| Ben's Bites | ✅ Working | Varies | RSS feed reliable |
| AI Rundown | ✅ Working | Varies | RSS feed reliable |
| CoinTelegraph | ✅ Working | 10-15 | High volume crypto news |
| Decrypt | ✅ Working | 5-10 | Quality crypto journalism |
| McKinsey | ⚠️ Timeout | N/A | RSS feed times out, needs alternative |
| HBR | ⚠️ Malformed | N/A | RSS XML parsing error, needs fix |

## 🛠️ Technical Details

### Scraper Output Schema
All scrapers conform to a consistent JSON schema:
```json
{
  "source": "source_name",
  "scrape_timestamp": "2026-02-16T05:00:00Z",
  "articles": [
    {
      "id": "unique_id",
      "source": "source_name",
      "title": "Article Title",
      "url": "https://...",
      "summary": "Article summary...",
      "published_at": "2026-02-16T04:00:00Z",
      "author": "Author Name",
      "is_saved": false
    }
  ],
  "errors": [],
  "success": true
}
```

### Dependencies
- `feedparser` - RSS/Atom feed parsing
- `python-dateutil` - Date parsing and manipulation
- `requests` - HTTP requests (if needed)

## 🎨 Design System

### Colors
- **Primary Purple**: `#6C5CE7` → `#A29BFE` (gradient)
- **KW Black**: `#1A1A1A`
- **KW Gold**: `#D4AF37`
- **Crypto Orange**: `#F7931A`
- **Consulting Teal**: `#0D9488`

### Typography
- **Primary**: Inter (Google Fonts)
- **Accent**: Outfit (Google Fonts)

## 📝 Development Roadmap

### Phase 5B: Deployment (Next)
- [ ] Fix McKinsey & HBR RSS feeds
- [ ] Create aggregation script for all scrapers
- [ ] Set up Supabase for persistent storage
- [ ] Implement 24-hour refresh automation
- [ ] Deploy to production (Vercel/Netlify)

### Future Enhancements
- [ ] Add Reddit scrapers (r/artificial, r/MachineLearning)
- [ ] Add Twitter/X integration
- [ ] Email digest feature
- [ ] Dark/light mode toggle
- [ ] Export articles to PDF
- [ ] Mobile app (React Native)

## 🤝 Contributing

This is a personal project, but suggestions are welcome! Feel free to open issues or submit pull requests.

## 📄 License

MIT License - feel free to use this project as inspiration for your own news aggregator!

## 🙏 Acknowledgments

- **News Sources**: Ben's Bites, AI Rundown, CoinTelegraph, Decrypt, McKinsey, HBR
- **Design Inspiration**: Modern dashboard UI/UX best practices
- **Built with**: HTML, CSS, JavaScript, Python

---

**Built with ❤️ by KW** | [Your Website] | [Your Twitter]
