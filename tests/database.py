from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError


# MySQL Database URL (example: using mysqlclient)
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:welcome1516@localhost/test_db"

# Creating the engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True  # echo=True to show SQL log output
)

# Creating session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# 이게 필요한가?
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_label)s",
    "fk": "fk_%(table_name)s_%(column_0_label)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base.metadata = MetaData(naming_convention=naming_convention)


# Dependency for DB connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Check if the database connection is successful
def check_db_connection():
    try:
        # Attempt to connect to the database
        connection = engine.connect()
        print("Database connected successfully!")
        connection.close()  # Close the connection after checking
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")


# Call the function to check the connection
if __name__ == "__main__":
    check_db_connection()
