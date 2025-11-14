# filepath: /Users/bharathkumarveeramalli/healthcare_platform-2/provider-service/src/database/seed.py
from sqlalchemy.orm import Session
from src.models.provider import Provider
from src.database.session import get_db
import logging

logger = logging.getLogger(__name__)

SAMPLE_PROVIDERS = [
    {
        "name": "Dr. Sarah Johnson",
        "specialty": "Cardiology",
        "qualification": "MD, FACC",
        "experience_years": 15,
        "rating": 4.8,
        "available": True,
        "consultation_fee": 150.00,
        "address": "123 Heart Center, Medical Plaza, Suite 401",
        "phone": "+1-555-0101",
        "email": "dr.johnson@healthcare.com"
    },
    {
        "name": "Dr. Michael Chen",
        "specialty": "Cardiology",
        "qualification": "MD, PhD",
        "experience_years": 20,
        "rating": 4.9,
        "available": True,
        "consultation_fee": 200.00,
        "address": "456 Cardiac Care Center, Floor 3",
        "phone": "+1-555-0102",
        "email": "dr.chen@healthcare.com"
    },
    {
        "name": "Dr. Jennifer Lee",
        "specialty": "Cardiology",
        "qualification": "MD, Interventional Cardiology",
        "experience_years": 13,
        "rating": 4.8,
        "available": True,
        "consultation_fee": 175.00,
        "address": "369 Advanced Heart Care",
        "phone": "+1-555-0109",
        "email": "dr.lee@healthcare.com"
    },
    {
        "name": "Dr. Emily Rodriguez",
        "specialty": "Dermatology",
        "qualification": "MD, Board Certified",
        "experience_years": 12,
        "rating": 4.7,
        "available": True,
        "consultation_fee": 120.00,
        "address": "789 Skin Care Clinic, Medical Building A",
        "phone": "+1-555-0103",
        "email": "dr.rodriguez@healthcare.com"
    },
    {
        "name": "Dr. Thomas Brown",
        "specialty": "Dermatology",
        "qualification": "MD, Dermatologic Surgery",
        "experience_years": 11,
        "rating": 4.6,
        "available": True,
        "consultation_fee": 130.00,
        "address": "741 Skin Wellness Center",
        "phone": "+1-555-0110",
        "email": "dr.brown@healthcare.com"
    },
    {
        "name": "Dr. James Wilson",
        "specialty": "Neurology",
        "qualification": "MD, FAAN",
        "experience_years": 18,
        "rating": 4.9,
        "available": True,
        "consultation_fee": 180.00,
        "address": "321 Brain & Spine Institute",
        "phone": "+1-555-0104",
        "email": "dr.wilson@healthcare.com"
    },
    {
        "name": "Dr. Lisa Anderson",
        "specialty": "Orthopedics",
        "qualification": "MD, FAAOS",
        "experience_years": 14,
        "rating": 4.6,
        "available": True,
        "consultation_fee": 160.00,
        "address": "654 Joint & Bone Center",
        "phone": "+1-555-0105",
        "email": "dr.anderson@healthcare.com"
    },
    {
        "name": "Dr. Robert Kim",
        "specialty": "Pediatrics",
        "qualification": "MD, FAAP",
        "experience_years": 10,
        "rating": 4.8,
        "available": True,
        "consultation_fee": 100.00,
        "address": "987 Children's Health Center",
        "phone": "+1-555-0106",
        "email": "dr.kim@healthcare.com"
    },
    {
        "name": "Dr. Amanda White",
        "specialty": "Psychiatry",
        "qualification": "MD, Board Certified",
        "experience_years": 16,
        "rating": 4.7,
        "available": True,
        "consultation_fee": 140.00,
        "address": "147 Mental Health Clinic",
        "phone": "+1-555-0107",
        "email": "dr.white@healthcare.com"
    },
    {
        "name": "Dr. David Martinez",
        "specialty": "General Practice",
        "qualification": "MD, Family Medicine",
        "experience_years": 8,
        "rating": 4.5,
        "available": True,
        "consultation_fee": 90.00,
        "address": "258 Primary Care Associates",
        "phone": "+1-555-0108",
        "email": "dr.martinez@healthcare.com"
    }
]

def seed_providers(db: Session):
    """Seed the database with sample providers"""
    try:
        # Check if we already have providers
        existing_count = db.query(Provider).count()
        
        if existing_count > 0:
            logger.info(f"Database already has {existing_count} providers. Skipping seed.")
            return
        
        # Add sample providers
        for provider_data in SAMPLE_PROVIDERS:
            provider = Provider(**provider_data)
            db.add(provider)
        
        db.commit()
        logger.info(f"✅ Successfully seeded {len(SAMPLE_PROVIDERS)} providers")
        
    except Exception as e:
        logger.error(f"❌ Error seeding providers: {e}")
        db.rollback()
        raise
