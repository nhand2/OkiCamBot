from decouple import config
from bot_helper import UID_ENUM

class Settings():
    
    OKI_BOT_COMMAND_PREFIX = config('OKI_BOT_COMMAND_PREFIX')
    SECRET_COMMAND = config('SECRET_COMMAND')
    YELP_API_KEY=config('YELP_API_KEY')
    APEX_API_KEY=config('APEX_API_KEY')
    
    USER_UIDS = {
        UID_ENUM.OKI:config('OKI_UID'),
        UID_ENUM.DEREK:config('DEREK_UID'),
        UID_ENUM.JON:config('JON_UID'),
        UID_ENUM.SOAP:config('SOAP_UID'),
        UID_ENUM.NAM:config('NAM_UID'),
        UID_ENUM.FANFAN:config('FANFAN_UID')
    }