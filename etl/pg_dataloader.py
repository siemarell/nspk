import psycopg2
import etl.config
from db.db import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

class Loader:
    def __init__(self):
        self._engine = create_engine(etl.config.conn_string)
        self._Session = sessionmaker(bind=self._engine)
        self.session = self._Session()
        
    def process_server_data(self, json):
        hosts = json['hosts']
        triggers = json['triggers']
        fails = json['fails']

        self.process_hosts(hosts)
        self.process_triggers(triggers)
        self.process_serv_fails(fails)

        try:
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()


    def process_serv_fails(self, fails):
        for fail in fails:
            triggerId = fail['triggerid']

            trigger = self.session.query(DTrigger).filter(DTrigger.external_id == int(triggerId)).one_or_none()
            host = self.session.query(DHost).filter(DHost.external_id == int(trigger.host_id)).one_or_none()
            dtime_start = datetime.datetime.fromtimestamp(int(fail['period'][0]))
            dtime_end = datetime.datetime.fromtimestamp(int(fail['period'][1]))

            kwargs = {
                "d_host": host,
                "d_trigger": trigger,
                "id_date_start": dtime_start.date(),
                "id_date_end": dtime_end.date(),
                "id_time_start": ts(dtime_start.time()),
                "id_time_end": ts(dtime_end.time()),
                "fact_timedelta": (dtime_end - dtime_start).seconds
            }

            try:
                id = self.session.query(FServIncident).filter(FServIncident.external_id == int(fail.id)).one_or_none().id
                kwargs['id'] = id
                dbFail = self.session.merge(FServIncident(**kwargs))
            except:
                dbFail = FServIncident(**kwargs)
            self.session.add(dbFail)


    def process_hosts(self, hosts):
        for hostId, host in hosts.items():
            # Find host and update or create a new one
            kwargs = {
                "name":host['name'],
                "purpose":host['role'],
                "division_owner":host['owner.person'],
                "subsystem":'',
                "platform_type":host['type'],
                "os":host['os'],
                "administrator":host['owner.person'],
                "external_id":int(hostId)
            }
            try:
                id = self.session.query(DHost).filter(DHost.external_id == int(hostId)).one_or_none().id
                kwargs['id'] = id
                dbHost = self.session.merge(DHost(**kwargs))
            except:
                dbHost = DHost(**kwargs)
            self.session.add(dbHost)
                

    def process_triggers(self, triggers):
        for triggerId, trigger in triggers.items():
            # Find trigger and update or create a new one
            kwargs = {
                "name":trigger['description'],
                "source_name": ','.join(trigger['role']),
                "external_id":int(triggerId)
            }
            try:
                id = self.session.query(DTrigger).filter(DTrigger.external_id == int(triggerId)).one_or_none().id
                kwargs['id'] = id
                dbTrigger = self.session.merge(DTrigger(**kwargs))
            except:
                dbTrigger = DTrigger(**kwargs)
            self.session.add(dbTrigger)

    def process_channel_data(self, json):
        clients = json['hosts']
        triggers = json['triggers']
        fails = json['fails']

        self.process_clients(clients)
        self.process_channel_fails(fails)

        try:
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()

    def process_clients(self, clients):
        pass

    def process_channel_fails(self, fails):
        pass


def ts(t):
    return t.hour * 3600 + t.minute * 60 + t.second