from app import create_app

app = create_app()

# This block is ONLY for when you run "python app.py" locally for development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)