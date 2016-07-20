from errbot import BotPlugin, botcmd, arg_botcmd, webhook
from datetime import datetime
import argparse

class ConcordTrack(BotPlugin):
    """
    Track CONCORD so your brain doesn't have to.
    """
    def activate(self):
        """
        Triggers on plugin activation
        """
        self.log.info('Activating ConcordTrack Plugin.')
        super(ConcordTrack, self).activate()
        
        if not "PREPPED_SYSTEMS" in self:
            self.clear_prepped_hash()
        self.start_poller(60, self.check_downtime)
        

    def clear_prepped_hash(self):
        self.log.info("Clearing prepped systems hash.")
        self["PREPPED_SYSTEMS"] = {
            'systems': {},
            'updated_at': datetime.utcnow()
        }

    def check_downtime(self):
        ps = self["PREPPED_SYSTEMS"]
        last_update = ps['updated_at']
        now = datetime.utcnow()
        dt = now.replace(hour=11, minute=00, second=0, microsecond=0)
        if last_update < dt and now > dt:
            self.log.info("It's downtime time! Resetting pulled systems.")
            self.clear_prepped_hash()

    @arg_botcmd('system', type=str, nargs=argparse.REMAINDER)
    @arg_botcmd('pulled_for', type=int)
    def pull(self, message, pulled_for, system):
        """Mark system as pulled for an amount of characters"""
        ps = self["PREPPED_SYSTEMS"]
        system = " ".join(system).title()
        person = str(message.frm.client)
        
        ps['systems'][system] = {
            'updated_at': datetime.utcnow(),
            'updated_by': person,
            'pulled_for': pulled_for
        }
        
        ps['updated_at'] = datetime.utcnow()
        self["PREPPED_SYSTEMS"] = ps
        return "{} marked as pulled for {} characters by {}".format(system, pulled_for, person)

    @botcmd
    def listpulled(self, message, args):
        """List all systems and the number they are pulled for"""
        ps = self["PREPPED_SYSTEMS"]
        result = ["The following systems are pulled:"]
        for system, info in ps['systems'].items():
            fr = info['pulled_for']
            at = info['updated_at']
            result.append("{}: {} at {}".format(system, fr, at.strftime("%H:%M:%S")))
        if len(result) > 1:
            return "\n".join(result)
        else:
            return "No systems currently marked as pulled"
            
    @botcmd
    def resetallpulled(self, message, args):
        """Reset All Pulled Systems!"""
        self.clear_prepped_hash()
        return "Pulled systems reset"
    
    @arg_botcmd('system', type=str)
    def ispulled(self, message, system):
        ps = self["PREPPED_SYSTEMS"]['systems']
        system = system.title()
        if not system in ps:
            return "{} is not marked as pulled".format(system)
        else:
            info = ps[system]
            fr = info['pulled_for']
            by = info['updated_by']
            at = info['updated_at']
            return "{} marked as pulled for {} characters by {} on {}".format(system, fr, by, at.strftime("%H:%M:%S"))

    @arg_botcmd('system', type=str)
    def resetpull(self, message, system):
        ps = self["PREPPED_SYSTEMS"]
        system = system.title()
        if not system in ps['systems']:
            return "{} is not marked as pulled".format(system)
        else:
            del ps['systems'][system]
            self["PREPPED_SYSTEMS"] = ps
            return "{} marked as unpulled".format(system)
