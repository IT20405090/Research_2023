from pymongo import MongoClient

# Function to establish a connection to the MongoDB database
def connect_to_database():

    #MongoDB connection details 
    client = MongoClient("mongodb+srv://it20405090:j030Ndw8@predictions.nvnsowv.mongodb.net/?retryWrites=true&w=majority")
    db = client["growth_prediction"]
    return db

def get_milestone_data(age):
    db = connect_to_database()
    collection = db["milestones"]
    query = {"age": age}
    milestone_data = collection.find_one(query)
    return milestone_data  # Return the whole document as a dictionary


def insert_milestone_data(age, emotional, language, cognitive, physical):
    db = connect_to_database()  # Use the same connection approach
    milestones_collection = db["milestones"]

    milestone_data = {
        "age": age,
        "emotional": ", ".join(emotional),  # Convert list to comma-separated string
        "language": ", ".join(language),    # Convert list to comma-separated string
        "cognitive": ", ".join(cognitive),  # Convert list to comma-separated string
        "physical": ", ".join(physical)     # Convert list to comma-separated string
    }

    milestones_collection.insert_one(milestone_data)
    print("Milestone data added successfully")
  
def update_milestone_data(age, emotional, language, cognitive, physical):
    db = connect_to_database()
    milestones_collection = db["milestones"]

    # Query to update milestone data for the given age
    query = {"age": age}

    # New data to be updated
    new_data = {
        "$set": {
            "emotional": ", ".join(emotional),
            "language": ", ".join(language),
            "cognitive": ", ".join(cognitive),
            "physical": ", ".join(physical)
        }
    }

    # Update the milestone data
    milestones_collection.update_one(query, new_data)
    print("Milestone data updated successfully")

def get_all_milestones():
    db = connect_to_database()
    milestones_collection = db["milestones"]

    # Retrieve all milestone documents
    all_milestones = list(milestones_collection.find({}))

    # Convert the milestone data into a list of dictionaries
    milestone_list = []
    for milestone in all_milestones:
        milestone_data = {
            "age": milestone["age"],
            "emotional": milestone["emotional"].split(", "),
            "language": milestone["language"].split(", "),
            "cognitive": milestone["cognitive"].split(", "),
            "physical": milestone["physical"].split(", ")
        }
        milestone_list.append(milestone_data)

    return milestone_list