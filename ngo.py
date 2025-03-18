from pymongo import MongoClient

# MongoDB connection URI
client = MongoClient("mongodb+srv://vedant:vedant@cluster0.1fi6w.mongodb.net/db")

# Access the database and collection
db = client['db']
ngos_collection = db['ngos']

# Sample NGO data from PCMC region
ngo_data = [
    {
        "name": "Helping Hands Foundation",
        "desc": "Support for underprivileged children.",
        "causes": ["Education", "Healthcare"],
        "location": "Pimpri-Chinchwad",
        "contact": "helpinghands@example.com",
        "image_url": "https://example.com/image1.jpg",
        "about": "Providing education and healthcare to children in need.",
        "phone": "9876543210"
    },
    {
        "name": "Green Earth Society",
        "desc": "Environment conservation and awareness.",
        "causes": ["Environment", "Sustainability"],
        "location": "Pimpri-Chinchwad",
        "contact": "greenearth@example.com",
        "image_url": "https://example.com/image2.jpg",
        "about": "Working towards a greener and cleaner city.",
        "phone": "9123456789"
    },
    {
        "name": "Food for All",
        "desc": "Providing meals to the homeless and needy.",
        "causes": ["Hunger Relief", "Community Support"],
        "location": "Pimpri-Chinchwad",
        "contact": "foodforall@example.com",
        "image_url": "https://example.com/image3.jpg",
        "about": "Ensuring no one sleeps hungry.",
        "phone": "8765432109"
    }
]

# Insert data into the collection
ngos_collection.insert_many(ngo_data)

print("NGO data inserted successfully.")
