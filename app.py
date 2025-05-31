from flask import Flask, render_template

app = Flask(__name__)

posts = [
    {
        'author': 'John Doe',
        'title': 'First Post',
        'content': 'This is the content of the first post.',
        'date_posted': 'April 20, 2023'
    },
    {
        'author': 'Jane Smith',
        'title': 'Second Post',
        'content': 'This is the content of the second post.',
        'date_posted': 'April 21, 2023'
    }
]

@app.route('/')
def home():
    return render_template('homepage.html', posts=posts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)