from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class Meal(Base):
    __tablename__ = "meals"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(String, default="default")  # ← nuevo
    meal_type    = Column(String, default="comida")
    description  = Column(String, default="sin detalle")
    calories     = Column(Float, default=0)
    protein      = Column(Float, default=0)
    carbs        = Column(Float, default=0)
    fats         = Column(Float, default=0)
    magnesio_mg  = Column(Float, default=0)
    zinc_mg      = Column(Float, default=0)
    hierro_mg    = Column(Float, default=0)
    calcio_mg    = Column(Float, default=0)
    potasio_mg   = Column(Float, default=0)
    sodio_mg     = Column(Float, default=0)
    vitamina_c_mg     = Column(Float, default=0)
    vitamina_d_iu     = Column(Float, default=0)
    vitamina_b12_mcg  = Column(Float, default=0)
    omega3_g     = Column(Float, default=0)
    created_at   = Column(DateTime, default=datetime.now)

class MacroGoal(Base):
    __tablename__ = "macro_goals"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(String, default="default")  # ← nuevo
    calories  = Column(Float, default=2200)
    protein   = Column(Float, default=160)
    carbs     = Column(Float, default=250)
    fats      = Column(Float, default=70)