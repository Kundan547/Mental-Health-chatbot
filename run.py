from ChatbotWebsite import create_app

# Create the app
app = create_app()

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
