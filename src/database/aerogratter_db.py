class AeroGratterDb():
    def __init__(self, db_client):
        self.db = db_client['aerogratterdb']
        
    def insert(self, subscriber, origin, dest):
        try:
            if self.db['subscribers'].find_one({'user_id': {'$eq': subscriber.id}, 'origin': {'$eq': origin}, 'dest': {'$eq': dest}}) is not None:
                return False
        except Exception as e:
            print (e)
            raise e
        
        item = {'user_id': subscriber.id, 'origin': origin, 'dest': dest, 'class': ['Y', 'J', 'F']}
        
        try:
            ret = self.db['subscribers'].insert_one(item)
        except Exception as e:
            print(e)
            raise e
        return ret.acknowledged
    
    def get_subscribed_count(self, origin, dest):
        try:
            count = self.db['subscribers'].count_documents({'origin': {'$eq': origin}, 'dest':{'$eq': dest}})
            return count
        except Exception as e:
            print(e)
            return 0
    
    def get_all_subscribers(self):
        try:
            subs = self.db['subscribers'].find()
            return list(subs)
        except:
            return list({})