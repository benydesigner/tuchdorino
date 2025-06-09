from fastapi import FastAPI
from app.routers import vehicles_router, auth_router # Import the new router
from app.core.database import engine, Base # For creating tables if not using Alembic for it

# Base.metadata.create_all(bind=engine) # This line creates tables directly; Alembic is preferred.

app = FastAPI(title='Vehicle Manager API')

app.include_router(auth_router, prefix='/api/v1/auth', tags=['authentication'])
app.include_router(vehicles_router, prefix='/api/v1', tags=['vehicles']) # Prefixing with /api/v1

@app.get('/')
def read_root():
    return {'message': 'Welcome to Vehicle Manager API'}

# Add a basic check if the database is accessible (optional)
# from app.core.database import SessionLocal
# @app.on_event('startup')
# async def startup_db_client():
#     try:
#         db = SessionLocal()
#         db.execute('SELECT 1') # Simple query to check connection
#         print('Database connection successful.')
#     except Exception as e:
#         print(f'Error connecting to the database: {e}')
#     finally:
#         if db:
#             db.close()
