import os
import sqlite3
import platform
import webbrowser

def setup_database():
    """Check and set up the database with required tables if they don't exist"""
    
    db_path = "jarvis.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Creating new database at {db_path}")
    else:
        print(f"Using existing database at {db_path}")
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sys_command table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sys_command (
        id INTEGER PRIMARY KEY, 
        name VARCHAR(100), 
        path VARCHAR(1000)
    )
    """)
    
    # Create web_command table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS web_command (
        id INTEGER PRIMARY KEY, 
        name VARCHAR(100), 
        url VARCHAR(1000)
    )
    """)
    
    # Create contacts table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY, 
        name VARCHAR(200), 
        Phone VARCHAR(255), 
        email VARCHAR(255) NULL
    )
    """)
    
    # Create search_engines table for dynamic searches
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_engines (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        url_template VARCHAR(1000)
    )
    """)
    
    # Insert common web commands if they don't exist
    web_commands = [
        ('youtube', 'https://www.youtube.com'),
        ('google', 'https://www.google.com'),
        ('gmail', 'https://mail.google.com'),
        ('maps', 'https://maps.google.com'),
        ('github', 'https://github.com'),
        ('stackoverflow', 'https://stackoverflow.com'),
        ('netflix', 'https://www.netflix.com'),
        ('amazon', 'https://www.amazon.com'),
        ('twitter', 'https://twitter.com'),
        ('facebook', 'https://www.facebook.com'),
        ('linkedin', 'https://www.linkedin.com'),
        ('reddit', 'https://www.reddit.com')
    ]
    
    for name, url in web_commands:
        cursor.execute("SELECT COUNT(*) FROM web_command WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO web_command VALUES (NULL, ?, ?)", (name, url))
    
    # Insert search engine templates
    search_engines = [
        ('google search', 'https://www.google.com/search?q={}'),
        ('youtube search', 'https://www.youtube.com/results?search_query={}'),
        ('amazon search', 'https://www.amazon.com/s?k={}'),
        ('bing search', 'https://www.bing.com/search?q={}'),
        ('duckduckgo search', 'https://duckduckgo.com/?q={}'),
        ('github search', 'https://github.com/search?q={}'),
        ('wikipedia search', 'https://en.wikipedia.org/wiki/Special:Search?search={}'),
        ('maps search', 'https://www.google.com/maps/search/{}'),
        ('stackoverflow search', 'https://stackoverflow.com/search?q={}'),
        ('reddit search', 'https://www.reddit.com/search/?q={}')
    ]
    
    for name, url_template in search_engines:
        cursor.execute("SELECT COUNT(*) FROM search_engines WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO search_engines VALUES (NULL, ?, ?)", (name, url_template))
    
    # Add common mac applications if on macOS
    if platform.system() == "Darwin":
        mac_apps = [
            ('safari', '/Applications/Safari.app'),
            ('photos', '/Applications/Photos.app'),
            ('music', '/Applications/Music.app'),
            ('messages', '/Applications/Messages.app'),
            ('facetime', '/Applications/FaceTime.app'),
            ('calendar', '/Applications/Calendar.app'),
            ('notes', '/Applications/Notes.app'),
            ('reminders', '/Applications/Reminders.app'),
            ('terminal', '/Applications/Utilities/Terminal.app'),
            ('calculator', '/Applications/Calculator.app')
        ]
        
        for name, path in mac_apps:
            if os.path.exists(path):
                cursor.execute("SELECT COUNT(*) FROM sys_command WHERE name = ?", (name,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO sys_command VALUES (NULL, ?, ?)", (name, path))
    
    # Create helper functions table (stored procedures)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS helper_functions (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        description TEXT
    )
    """)
    
    # Insert helper functions
    helper_functions = [
        ('search', 'Perform a web search using Google'),
        ('play_youtube', 'Search and play a video on YouTube'),
        ('open_website', 'Open a specific website'),
        ('open_app', 'Open a system application'),
        ('find_contact', 'Search for a contact in the database')
    ]
    
    for name, description in helper_functions:
        cursor.execute("SELECT COUNT(*) FROM helper_functions WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO helper_functions VALUES (NULL, ?, ?)", (name, description))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Database setup complete.")

def perform_web_search(query, engine='google search'):
    """
    Perform a web search using the specified search engine
    """
    conn = sqlite3.connect("jarvis.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT url_template FROM search_engines WHERE name = ?", (engine,))
        result = cursor.fetchone()
        
        if result:
            url_template = result[0]
            search_url = url_template.format(query.replace(' ', '+'))
            webbrowser.open(search_url)
            return True
        else:
            # Default to Google if engine not found
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return True
    except Exception as e:
        print(f"Error performing search: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()
    
    # Test the search functionality
    # perform_web_search("python programming")