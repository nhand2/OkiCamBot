from pymongo import MongoClient

from datetime import datetime


class ReminderDb:
    def __init__(self, db_client):
        self.db = db_client["reminderdb"]

    def insert(self, member, reminder, date):
        item = {"user_id": member.id, "reminder": reminder, "date": date, "sent": False}
        print(item)
        ret = self.db["reminders"].insert_one(item)
        return ret.acknowledged

    def check_reminders(self):
        currentTime = datetime.now()

        updatedReminders = self.db["reminders"].update_many(
            {"date": {"$lte": currentTime}}, {"$set": {"sent": True}}
        )

        if updatedReminders.matched_count == 0:
            print("No reminders to send")
            return list({})

        return self.db["reminders"].find({"sent": {"$eq": True}})

    def remove_sent_reminders(self):
        ret = self.db["reminders"].delete_many({"sent": {"$eq": True}})

        print(f"Deleted {ret.deleted_count} documents!")

        return ret.acknowledged
