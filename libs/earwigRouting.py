from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

dbtype = "sqlite"
ip = "localhost"
port = "8000"
dbName = "EWEngine"
username = "username"
password = "password"
authdns = f'{username}{f":{password}" if password != "" else ""}@{ip}:{port}'

engine = create_engine(
	f"{dbtype}://{authdns}/EWEngine"
)

Session = sessionmaker(
	bind=engine
)

Base = declarative_base()

class EWRoute(Base):
	__tablename__ = "ewRoute"
	
	id = Column(Integer, primary_key=True)
	route = Column(String, nullable=False)
	path = Column(String, nullable=False)