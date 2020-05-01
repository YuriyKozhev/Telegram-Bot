class Config:
    PRODUCTION_CONFIG = 'PROD'
    LOCAL_CONFIG = 'LOCAL'
    SERVER_CONFIG = 'SERVER'
    
class ServerConfig(Config):
    
    def __init__(self):
        self.CONFIG_NAME = Config.SERVER_CONFIG 
        
        import os
        self.TOKEN = os.environ['TOKEN']
        self.DATABASE_URL = os.environ['DATABASE_URL']
        
        from urllib.parse import urlparse
        result = urlparse(self.DATABASE_URL)
        self.BD_USERNAME = result.username
        self.BD_PASSWORD = result.password
        self.BD_DATABASE = result.path[1:]
        self.BD_HOSTNAME = result.hostname
    