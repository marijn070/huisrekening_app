from sqlmodel import Session, SQLModel, create_engine, text

sqlite_file_name = "./database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))  # for SQLite only


def get_session():
    with Session(engine) as session:
        yield session
