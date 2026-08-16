import os
import bcrypt
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///eco_buddy.db")
DB_NAME = "eco_buddy.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, default=1)
    date = Column(DateTime, default=datetime.utcnow)
    transport = Column(String)
    distance = Column(Float)
    electricity = Column(Float)
    diet = Column(String)
    flights = Column(Integer)
    footprint = Column(Float)
    eco_score = Column(Integer)

class Appliance(Base):
    __tablename__ = "appliances"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String)
    category = Column(String)
    quantity = Column(Integer)
    power_rating_watts = Column(Float)
    hours_used_per_day = Column(Float)
    standby_draw_watts = Column(Float)
    usage_schedule = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SolarConfig(Base):
    __tablename__ = "solar_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    roof_space_m2 = Column(Float)
    peak_sun_hours = Column(Float)
    utility_rate_per_kwh = Column(Float)
    panel_efficiency = Column(Float)
    installation_cost_per_kw = Column(Float)
    maintenance_cost_per_year = Column(Float)
    annual_rate_increase = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserChallenge(Base):
    __tablename__ = "user_challenges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    challenge_id = Column(String, nullable=False)
    progress_value = Column(Float, default=0.0)
    status = Column(String, default='enrolled')
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    xp_awarded = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UnlockedBadge(Base):
    __tablename__ = "unlocked_badges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    badge_id = Column(String, nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    xp_awarded = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'badge_id', name='uix_user_badge'),)

class XpTransaction(Base):
    __tablename__ = "xp_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    source_type = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    xp_amount = Column(Integer, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'source_type', 'source_id', name='uix_user_source'),)

class JourneyProfile(Base):
    __tablename__ = "journey_profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    transport_mode = Column(String, nullable=False)
    passenger_count = Column(Integer, default=1)
    trips_per_week = Column(Integer, default=1)
    is_commute = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OffsetTransaction(Base):
    __tablename__ = "offset_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    project_id = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    offset_tonnes = Column(Float, nullable=False)
    cost_per_tonne = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    transaction_status = Column(String, default='completed')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WaterConsumption(Base):
    __tablename__ = "water_consumption"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    shower_mins_per_day = Column(Float)
    laundry_loads_per_week = Column(Float)
    dishwasher_runs_per_week = Column(Float)
    garden_mins_per_week = Column(Float)
    diet = Column(String)
    total_liters = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def to_dict(obj):
    if not obj:
        return None
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def to_tuple_assessments(obj):
    if not obj:
        return None
    # SQLite returns (id, user_id, date, transport, distance, electricity, diet, flights, footprint, eco_score)
    # The date string should match SQLite's default CURRENT_TIMESTAMP format if possible, but SQLAlchemy returns datetime objects.
    # We will return the values in exact column order of the original create table:
    # id, user_id, date, transport, distance, electricity, diet, flights, footprint, eco_score
    return (
        obj.id, obj.user_id, str(obj.date) if obj.date else None, obj.transport, 
        obj.distance, obj.electricity, obj.diet, obj.flights, obj.footprint, obj.eco_score
    )

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

def init_energy_db():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database energy init error: {e}")
        return False

def init_gamification_db():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database gamification init error: {e}")
        return False

def init_marketplace_db():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database marketplace init error: {e}")
        return False

def init_water_db():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database water init error: {e}")
        return False


def create_user(username, email, password):
    try:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        with SessionLocal() as session:
            new_user = User(username=username, email=email, password_hash=password_hash)
            session.add(new_user)
            session.commit()
            return new_user.id
    except Exception as e:
        print(f"create_user error: {e}")
        return None

def verify_user(username, password):
    try:
        with SessionLocal() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                    return user.id
        return None
    except Exception as e:
        print(f"verify_user error: {e}")
        return None

def save_assessment(user_id, transport, distance, electricity, diet, flights, footprint, eco_score):
    try:
        with SessionLocal() as session:
            ass = Assessment(
                user_id=user_id, transport=transport, distance=distance, electricity=electricity,
                diet=diet, flights=flights, footprint=footprint, eco_score=eco_score
            )
            session.add(ass)
            session.commit()
            return True
    except Exception as e:
        print(f"Database save error: {e}")
        return False

def get_assessments(user_id=1):
    try:
        with SessionLocal() as session:
            assessments = session.query(Assessment).filter(Assessment.user_id == user_id).all()
            # Ensure we return list of tuples for backwards compatibility with front-end
            return [(a.id, a.user_id, a.date, a.transport, a.distance, a.electricity, a.diet, a.flights, a.footprint, a.eco_score) for a in assessments]
    except Exception as e:
        print(f"Database read error: {e}")
        return []

def add_appliance(user_id, name, category, quantity, power_rating, hours_used, standby_draw):
    try:
        with SessionLocal() as session:
            app = Appliance(
                user_id=user_id, name=name, category=category, quantity=quantity,
                power_rating_watts=power_rating, hours_used_per_day=hours_used, standby_draw_watts=standby_draw
            )
            session.add(app)
            session.commit()
            return True
    except Exception as e:
        print(f"Appliance save error: {e}")
        return False

def delete_appliance(app_id):
    try:
        with SessionLocal() as session:
            app = session.query(Appliance).filter(Appliance.id == app_id).first()
            if app:
                session.delete(app)
                session.commit()
            return True
    except Exception as e:
        return False

def get_appliances(user_id):
    try:
        with SessionLocal() as session:
            results = session.query(Appliance).filter(Appliance.user_id == user_id).order_by(Appliance.created_at.desc()).all()
            return [to_dict(r) for r in results]
    except Exception as e:
        return []

def save_solar_config(user_id, roof_space, peak_sun_hours, utility_rate, panel_efficiency, install_cost, maint_cost, rate_inc):
    try:
        with SessionLocal() as session:
            session.query(SolarConfig).filter(SolarConfig.user_id == user_id).delete()
            config = SolarConfig(
                user_id=user_id, roof_space_m2=roof_space, peak_sun_hours=peak_sun_hours,
                utility_rate_per_kwh=utility_rate, panel_efficiency=panel_efficiency,
                installation_cost_per_kw=install_cost, maintenance_cost_per_year=maint_cost,
                annual_rate_increase=rate_inc
            )
            session.add(config)
            session.commit()
            return True
    except Exception as e:
        return False

def get_solar_config(user_id):
    try:
        with SessionLocal() as session:
            result = session.query(SolarConfig).filter(SolarConfig.user_id == user_id).first()
            return to_dict(result)
    except Exception as e:
        return None

def enroll_challenge(user_id, challenge_id):
    try:
        with SessionLocal() as session:
            existing = session.query(UserChallenge).filter(UserChallenge.user_id == user_id, UserChallenge.challenge_id == challenge_id, UserChallenge.status != 'expired').first()
            if existing:
                return False
            chal = UserChallenge(user_id=user_id, challenge_id=challenge_id, status='enrolled')
            session.add(chal)
            session.commit()
            return True
    except Exception as e:
        print(f"enroll_challenge error: {e}")
        return False

def update_challenge_progress(user_id, challenge_id, progress_increment=None, set_progress=None):
    try:
        with SessionLocal() as session:
            chal = session.query(UserChallenge).filter(UserChallenge.user_id == user_id, UserChallenge.challenge_id == challenge_id, UserChallenge.status == 'enrolled').first()
            if chal:
                if progress_increment is not None:
                    chal.progress_value += progress_increment
                elif set_progress is not None:
                    chal.progress_value = set_progress
                session.commit()
            return True
    except Exception as e:
        print(f"update_challenge_progress error: {e}")
        return False

def complete_challenge(user_id, challenge_id):
    try:
        with SessionLocal() as session:
            chal = session.query(UserChallenge).filter(UserChallenge.user_id == user_id, UserChallenge.challenge_id == challenge_id, UserChallenge.status == 'enrolled').first()
            if chal:
                chal.status = 'completed'
                chal.completed_at = datetime.utcnow()
                session.commit()
            return True
    except Exception as e:
        print(f"complete_challenge error: {e}")
        return False

def get_user_challenges(user_id):
    try:
        with SessionLocal() as session:
            results = session.query(UserChallenge).filter(UserChallenge.user_id == user_id).all()
            return [to_dict(r) for r in results]
    except Exception as e:
        return []

def award_xp(user_id, source_type, source_id, xp_amount, description):
    try:
        with SessionLocal() as session:
            xp = XpTransaction(user_id=user_id, source_type=source_type, source_id=source_id, xp_amount=xp_amount, description=description)
            session.add(xp)
            
            if source_type == 'challenge':
                session.query(UserChallenge).filter(UserChallenge.user_id == user_id, UserChallenge.challenge_id == source_id).update({"xp_awarded": True})
            elif source_type == 'badge':
                session.query(UnlockedBadge).filter(UnlockedBadge.user_id == user_id, UnlockedBadge.badge_id == source_id).update({"xp_awarded": True})
                
            session.commit()
            return True
    except Exception as e:
        print(f"award_xp error: {e}")
        return False

def get_total_xp(user_id):
    try:
        from sqlalchemy import func
        with SessionLocal() as session:
            total = session.query(func.sum(XpTransaction.xp_amount)).filter(XpTransaction.user_id == user_id).scalar()
            return total if total else 0
    except Exception:
        return 0

def unlock_badge_in_db(user_id, badge_id):
    try:
        with SessionLocal() as session:
            badge = UnlockedBadge(user_id=user_id, badge_id=badge_id)
            session.add(badge)
            session.commit()
            return True
    except Exception as e:
        print(f"unlock_badge_in_db error: {e}")
        return False

def get_unlocked_badges(user_id):
    try:
        with SessionLocal() as session:
            results = session.query(UnlockedBadge).filter(UnlockedBadge.user_id == user_id).all()
            return [to_dict(r) for r in results]
    except Exception:
        return []

def save_journey_profile(user_id, name, distance_km, transport_mode, passenger_count, trips_per_week, is_commute):
    try:
        with SessionLocal() as session:
            profile = JourneyProfile(
                user_id=user_id, name=name, distance_km=distance_km, transport_mode=transport_mode,
                passenger_count=passenger_count, trips_per_week=trips_per_week, is_commute=bool(is_commute)
            )
            session.add(profile)
            session.commit()
            return True
    except Exception as e:
        print(f'save_journey_profile error: {e}')
        return False

def get_journey_profiles(user_id):
    try:
        with SessionLocal() as session:
            results = session.query(JourneyProfile).filter(JourneyProfile.user_id == user_id).order_by(JourneyProfile.created_at.desc()).all()
            return [to_dict(r) for r in results]
    except Exception:
        return []

def delete_journey_profile(profile_id):
    try:
        with SessionLocal() as session:
            session.query(JourneyProfile).filter(JourneyProfile.id == profile_id).delete()
            session.commit()
            return True
    except Exception:
        return False

def save_offset_transaction(user_id, project_id, project_name, offset_tonnes, cost_per_tonne, total_cost, transaction_status='completed'):
    try:
        with SessionLocal() as session:
            txn = OffsetTransaction(
                user_id=user_id, project_id=project_id, project_name=project_name, offset_tonnes=offset_tonnes,
                cost_per_tonne=cost_per_tonne, total_cost=total_cost, transaction_status=transaction_status
            )
            session.add(txn)
            session.commit()
            return True
    except Exception as e:
        print(f'save_offset_transaction error: {e}')
        return False

def get_offset_transactions(user_id):
    try:
        with SessionLocal() as session:
            results = session.query(OffsetTransaction).filter(OffsetTransaction.user_id == user_id).order_by(OffsetTransaction.created_at.desc()).all()
            return [to_dict(r) for r in results]
    except Exception:
        return []

def delete_offset_transaction(transaction_id):
    try:
        with SessionLocal() as session:
            session.query(OffsetTransaction).filter(OffsetTransaction.id == transaction_id).delete()
            session.commit()
            return True
    except Exception:
        return False

def get_total_offsets(user_id):
    try:
        from sqlalchemy import func
        with SessionLocal() as session:
            total = session.query(func.sum(OffsetTransaction.offset_tonnes)).filter(OffsetTransaction.user_id == user_id, OffsetTransaction.transaction_status != 'reversed').scalar()
            return total if total else 0.0
    except Exception:
        return 0.0

def get_total_spend(user_id):
    try:
        from sqlalchemy import func
        with SessionLocal() as session:
            total = session.query(func.sum(OffsetTransaction.total_cost)).filter(OffsetTransaction.user_id == user_id, OffsetTransaction.transaction_status != 'reversed').scalar()
            return total if total else 0.0
    except Exception:
        return 0.0

def save_water_assessment(user_id, shower, laundry, dishwasher, garden, diet, total_liters):
    try:
        with SessionLocal() as session:
            water = WaterConsumption(
                user_id=user_id, shower_mins_per_day=shower, laundry_loads_per_week=laundry,
                dishwasher_runs_per_week=dishwasher, garden_mins_per_week=garden, diet=diet, total_liters=total_liters
            )
            session.add(water)
            session.commit()
            return True
    except Exception as e:
        print(f'save_water_assessment error: {e}')
        return False

def get_water_assessments(user_id):
    try:
        with SessionLocal() as session:
            results = session.query(WaterConsumption).filter(WaterConsumption.user_id == user_id).order_by(WaterConsumption.created_at.desc()).all()
            return [to_dict(r) for r in results]
    except Exception:
        return []
