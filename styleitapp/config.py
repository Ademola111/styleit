#the config that is not inside instance
class Config(object):
    DATABASE_URI="kg968nbfkk876 "
    MERCHANT_ID="SAMPLE"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://root@127.0.0.1/styleit"
    # SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://root@127.0.0.1/style"
    SQLALCHEMY_TRACK_MODIFICATIONS=True

    MERCHANT_ID="dg8765@hj#"

    

class Test_config(Config):
    DATABASE_URL="Test Connection parameters"