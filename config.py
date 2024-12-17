class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Mypassword@127.0.0.1/gushi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Mypassword'  # Utiliza una clave secreta para sesiones
