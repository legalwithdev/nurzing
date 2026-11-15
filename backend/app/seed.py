"""Seed the demo professionals. Run: python -m app.seed"""
from __future__ import annotations

from sqlalchemy import select

from .db import SessionLocal, init_db
from .models import Professional

# Demo records. Every name/rating/registration here is a PLACEHOLDER.
SEED = [
    # tier 1: B.Sc Nursing + RN&RM + experience + specialisation
    dict(slug="ananya-rao", name="Ananya Rao", designation="RN&RM Nurse (ICU)", qualification="B.Sc Nursing",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=8, city="Bengaluru", area="Koramangala",
         rate_paise=180000, rating=4.9, reviews_count=214, available_today=True, distance_km=2.4,
         care_types=["Home Nursing", "ICU-trained", "Post-Surgical"], languages=["English", "Hindi", "Kannada"]),
    dict(slug="fatima-sheikh", name="Fatima Sheikh", designation="RN&RM Nurse (Maternity)", qualification="B.Sc Nursing",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=6, city="Mumbai", area="Bandra",
         rate_paise=190000, rating=4.8, reviews_count=141, available_today=True, distance_km=4.2,
         care_types=["Mother & Baby", "Home Nursing"], languages=["English", "Hindi", "Marathi"]),
    dict(slug="imran-qureshi", name="Imran Qureshi", designation="RN&RM Nurse (ICU)", qualification="B.Sc Nursing",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=9, city="Delhi NCR", area="Saket",
         rate_paise=210000, rating=4.9, reviews_count=302, available_today=False, distance_km=6.1,
         care_types=["ICU-trained", "Home Nursing", "Post-Surgical"], languages=["English", "Hindi", "Urdu"]),
    dict(slug="sunita-joshi", name="Sunita Joshi", designation="RN&RM Nurse (Maternity)", qualification="B.Sc Nursing",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=7, city="Pune", area="Kothrud",
         rate_paise=175000, rating=4.8, reviews_count=188, available_today=True, distance_km=3.3,
         care_types=["Mother & Baby", "Home Nursing"], languages=["English", "Hindi", "Marathi"]),
    dict(slug="joseph-mathew", name="Joseph Mathew", designation="RN&RM Nurse (ICU)", qualification="B.Sc Nursing",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=10, city="Chennai", area="Adyar",
         rate_paise=220000, rating=4.9, reviews_count=267, available_today=True, distance_km=5.0,
         care_types=["ICU-trained", "Post-Surgical", "Home Nursing"], languages=["English", "Tamil", "Malayalam"]),
    # tier 2: RN&RM with GNM
    dict(slug="priya-deshmukh", name="Priya Deshmukh", designation="RN&RM Nurse (Post-Surgical)", qualification="GNM",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=5, city="Mumbai", area="Andheri",
         rate_paise=160000, rating=4.7, reviews_count=120, available_today=True, distance_km=3.8,
         care_types=["Home Nursing", "Post-Surgical"], languages=["English", "Hindi", "Marathi"]),
    dict(slug="lakshmi-reddy", name="Lakshmi Reddy", designation="RN&RM Nurse (Elderly Care)", qualification="GNM",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=11, city="Hyderabad", area="Jubilee Hills",
         rate_paise=150000, rating=4.8, reviews_count=231, available_today=False, distance_km=7.2,
         care_types=["Elderly Care", "Home Nursing"], languages=["English", "Telugu", "Hindi"]),
    dict(slug="grace-fernandes", name="Grace Fernandes", designation="RN&RM Nurse (Post-Surgical)", qualification="GNM",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=9, city="Bengaluru", area="Indiranagar",
         rate_paise=165000, rating=4.8, reviews_count=198, available_today=True, distance_km=4.5,
         care_types=["Home Nursing", "Post-Surgical"], languages=["English", "Hindi", "Konkani"]),
    dict(slug="divya-pillai", name="Divya Pillai", designation="RN&RM Nurse (Post-Surgical)", qualification="GNM",
         reg_type="RN&RM", reg_number=None, reg_verified=False, years=6, city="Chennai", area="T. Nagar",
         rate_paise=155000, rating=4.7, reviews_count=144, available_today=True, distance_km=2.9,
         care_types=["Home Nursing", "Post-Surgical"], languages=["English", "Tamil"]),
    # tier 3: other licensed profession
    dict(slug="meera-krishnan", name="Meera Krishnan", designation="Physiotherapist", qualification="BPT",
         reg_type="none", reg_number=None, reg_verified=False, years=7, city="Chennai", area="Adyar",
         rate_paise=90000, rating=4.8, reviews_count=141, available_today=True, distance_km=4.2,
         care_types=["Physiotherapy"], languages=["English", "Tamil"]),
    # tier 4: non-medical support
    dict(slug="rakesh-nair", name="Rakesh Nair", designation="Attendant / Caregiver", qualification="",
         reg_type="none", reg_number=None, reg_verified=False, years=10, city="Bengaluru", area="Whitefield",
         rate_paise=90000, rating=4.6, reviews_count=176, available_today=True, distance_km=8.1,
         care_types=["Elderly Care", "Attendant"], languages=["English", "Hindi", "Malayalam"]),
    dict(slug="karan-singh", name="Karan Singh", designation="Attendant / Ward Boy", qualification="",
         reg_type="none", reg_number=None, reg_verified=False, years=8, city="Delhi NCR", area="Dwarka",
         rate_paise=100000, rating=4.6, reviews_count=265, available_today=True, distance_km=5.6,
         care_types=["Attendant", "Elderly Care"], languages=["English", "Hindi"]),
]


def run() -> int:
    init_db()
    with SessionLocal() as db:
        created = 0
        for row in SEED:
            if db.scalars(select(Professional).where(Professional.slug == row["slug"])).first():
                continue
            db.add(Professional(**row))
            created += 1
        db.commit()
        total = db.scalar(select(Professional).limit(1))
    print(f"seed: {created} professionals added")
    return created


if __name__ == "__main__":
    run()
