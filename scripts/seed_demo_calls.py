from services.database import init_db, create_call, add_message, update_call_status, update_call_score
import uuid
import time

def seed_demo_calls():
    print("Initializing DB and seeding demo calls...")
    init_db()
    
    # Demo Call 1: High Sentiment
    call_1 = "call_" + str(uuid.uuid4())[:8]
    create_call(call_1, "Rajesh Kumar", "+91 98765 43210")
    add_message(call_1, str(uuid.uuid4()), "customer", "Namaste, I am interested in the tractor loan.")
    add_message(call_1, str(uuid.uuid4()), "ai", "Namaste Rajesh! I can definitely help with that. Our Mahindra tractor loans start at 8.5% interest.")
    update_call_status(call_1, False)
    update_call_score(call_1, 9)
    
    # Demo Call 2: Medium Sentiment
    call_2 = "call_" + str(uuid.uuid4())[:8]
    create_call(call_2, "Anjali Sharma", "+91 87654 32109")
    add_message(call_2, str(uuid.uuid4()), "customer", "What are the crop insurance rates for this season?")
    add_message(call_2, str(uuid.uuid4()), "ai", "For Kharif crops, the premium is 2%. Would you like to hear more?")
    update_call_status(call_2, False)
    update_call_score(call_2, 6)
    
    print("Demo calls seeded successfully!")

if __name__ == "__main__":
    seed_demo_calls()
