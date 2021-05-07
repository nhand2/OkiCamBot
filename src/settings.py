from decouple import config

class Settings():
    
    OKI_BOT_COMMAND_PREFIX = config('OKI_BOT_COMMAND_PREFIX')
    OKI_UID = config('OKI_UID')
    DEREK_UID = config('DEREK_UID')
    JON_UID = config('JON_UID')
    SOAP_UID = config('SOAP_UID')
    NAM_UID = config('NAM_UID')
    SECRET_COMMAND = config('SECRET_COMMAND')
    YELP_API_KEY=config('YELP_API_KEY')