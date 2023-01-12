from database_pgs import Base, engine


Base.metadata.create_all(engine)
