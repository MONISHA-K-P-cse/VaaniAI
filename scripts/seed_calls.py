import sys
import os
import uuid

# Add the project root to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.database import init_db, create_call, add_message, update_call_status, update_call_score

def seed_demo_data():
    print("Seeding demo call data...")
    init_db()
    
    # Call 1: Anjali Sharma (English/Hindi mix)
    c1_id = "call_anjali_" + str(uuid.uuid4())[:8]
    create_call(c1_id, "Anjali Sharma", "+91 87654 32109")
    update_call_status(c1_id, False)
    update_call_score(c1_id, 9)
    
    add_message(c1_id, str(uuid.uuid4()), "customer", "Hello, I wanted to know about the crop insurance for this season.")
    add_message(c1_id, str(uuid.uuid4()), "ai", "Namaste Anjali Ji! For this Kharif season, the premium is 2%. Would you like me to help you with the registration?")
    add_message(c1_id, str(uuid.uuid4()), "customer", "Yes, what documents do I need?")
    add_message(c1_id, str(uuid.uuid4()), "ai", "You will need your Aadhaar card, land records (7/12 extract), and bank passbook. I can send you a WhatsApp link with more details.")
    
    # Call 2: Rajesh Kumar (Hindi)
    c2_id = "call_rajesh_" + str(uuid.uuid4())[:8]
    create_call(c2_id, "Rajesh Kumar", "+91 98765 43210")
    update_call_status(c2_id, False)
    update_call_score(c2_id, 7)
    
    add_message(c2_id, str(uuid.uuid4()), "customer", "Kya mujhe kisan credit card par loan mil sakta hai?")
    add_message(c2_id, str(uuid.uuid4()), "ai", "Ji haan Rajesh ji, KCC par aapko 3 lakh tak ka loan mil sakta hai. Aapke paas kisan bahi hai?")
    add_message(c2_id, str(uuid.uuid4()), "customer", "Haan, mere paas saare kagaz hain.")
    
    # Call 3: Suresh Gowda (Kannada)
    c3_id = "call_suresh_" + str(uuid.uuid4())[:8]
    create_call(c3_id, "Suresh Gowda", "+91 76543 21098")
    update_call_status(c3_id, False)
    update_call_score(c3_id, 8)
    
    add_message(c3_id, str(uuid.uuid4()), "customer", "ನಮಸ್ಕಾರ, ನನ್ನ ಬೆಳೆ ವಿಮೆಯ ಸ್ಥಿತಿ ಏನು?")
    add_message(c3_id, str(uuid.uuid4()), "ai", "ನಮಸ್ಕಾರ ಸುರೇಶ್ ಅವರೇ, ನಿಮ್ಮ ಬೆಳೆ ವಿಮೆಯ ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆಯಲ್ಲಿದೆ. ಇನ್ನು ಎರಡು ದಿನಗಳಲ್ಲಿ ನಿಮಗೆ ಮಾಹಿತಿ ಸಿಗುತ್ತದೆ.")

    print("Successfully seeded 3 demo calls!")

if __name__ == "__main__":
    seed_demo_data()
