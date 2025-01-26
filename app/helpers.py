from .models import SecurityHelper, SecureFeedback, CustomerFeedback
import datetime

def encrypt_customer_feedback(feedback):
    security_helper = SecurityHelper()
    print("Starting encryption process for customer feedback")
    encrypted_dek = security_helper.generate_encrypted_dek(feedback.email)
    print("Generated encrypted DEK:", encrypted_dek)
    
    encrypted_email = security_helper.encrypt(feedback.email, encrypted_dek)
    print("Encrypted email:", encrypted_email)
    
    encrypted_contact_number = security_helper.encrypt(feedback.contact_number, encrypted_dek)
    print("Encrypted contact number:", encrypted_contact_number)
    
    encrypted_feedback = security_helper.encrypt(feedback.feedback, encrypted_dek)
    print("Encrypted feedback:", encrypted_feedback)
    
    print("Encryption process completed for customer feedback")
    return SecureFeedback(
        customer_email=encrypted_email,
        contact_number=encrypted_contact_number,
        encrypted_feedback=encrypted_feedback,
        dek=encrypted_dek,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc)
    )

def decrypt_secure_feedback(secure_feedback):
    security_helper = SecurityHelper()
    print("Starting decryption process for secure feedback ID:", secure_feedback.id)
    
    email = security_helper.decrypt(secure_feedback.customer_email, secure_feedback.dek)
    print("Decrypted email:", email)
    
    contact_number = security_helper.decrypt(secure_feedback.contact_number, secure_feedback.dek)
    print("Decrypted contact number:", contact_number)
    
    feedback = security_helper.decrypt(secure_feedback.encrypted_feedback, secure_feedback.dek)
    print("Decrypted feedback:", feedback)
    
    print("Decryption process completed for secure feedback ID:", secure_feedback.id)
    return CustomerFeedback(email, contact_number, feedback)
