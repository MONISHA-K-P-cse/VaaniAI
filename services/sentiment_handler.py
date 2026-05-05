import uuid

def evaluate_intervention(sentiment: str) -> bool:
    """
    Determines if the detected sentiment warrants an intervention.
    """
    trigger_sentiments = ["frustrated", "skeptical", "angry", "annoyed"]
    return sentiment.lower() in trigger_sentiments

def trigger_discount_offer(context: dict = None) -> str:
    """
    Generates a targeted discount offer to retain a frustrated or skeptical user.
    """
    # In a real system, this would check business rules or user purchase history.
    # We mock a generic 10% discount for demonstration.
    discount_code = f"RETAIN-10-{str(uuid.uuid4())[:6].upper()}"
    return f"Offer the user a 10% discount using promo code: {discount_code}."
