from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["aml_database"]

kyc_collection = db["kyc_profiles"]
transaction_collection = db["transactions"]
results_collection = db["aml_results"]

print("MongoDB Connected")