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
    }
]

# Insert data into the collection
ngos_collection.insert_many(ngo_data)

print("NGO data inserted successfully.")
