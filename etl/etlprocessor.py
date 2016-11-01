import psycopg2
from . import config
from db.db import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import json

class EtlProcessor:
    def __init__(self):
        self._engine = create_engine(config.conn_string)
        self._Session = sessionmaker(bind=self._engine)
        self.session = self._Session()
        
    def process_server_data(self, json: dict) -> bool:
        hosts = json.get('hosts')
        triggers = json.get('triggers')
        fails = json.get('fails')

        for fail in fails:
            triggerId = fail['triggerid']
            hostId = triggers[triggerId]['hostid']
            failId = fail['events']['begin']
            trigger = self._get_trigger(triggers[triggerId], int(triggerId))
            host = self._get_host(hosts[hostId], int(hostId))

            dtime_start = datetime.datetime.fromtimestamp(int(fail['period'][0]))
            dtime_end = datetime.datetime.fromtimestamp(int(fail['period'][1]))

            kwargs = {
                "d_host": host,
                "event_start_id": failId,
                "d_trigger": trigger,
                "id_date_start": dtime_start.date(),
                "id_date_end": dtime_end.date(),
                "id_time_start": tm(dtime_start.time()),
                "id_time_end": tm(dtime_end.time()),
                "fact_timedelta": (dtime_end - dtime_start).seconds,
                "description": triggers[triggerId]['description']
            }
            dbFail = self.session.query(FServIncident).filter(FServIncident.event_start_id == int(failId)).one_or_none()
            if dbFail:
                id = dbFail.id
                kwargs['id'] = id
                dbFail = self.session.merge(FServIncident(**kwargs))
            else:
                dbFail = FServIncident(**kwargs)
            self.session.add(dbFail)

        try:
            self.session.commit()
            return True
        except Exception as e:
            print(e)
            self.session.rollback()
            return False

    def _get_trigger(self, triggerJson: dict, id) -> DTrigger:
        kwargs = {
            "source_name": ','.join(triggerJson.get('subsys')),
            "external_id": id
        }
        trigger = self.session.query(DTrigger).filter(DTrigger.external_id == id).one_or_none()
        if trigger:
            id = trigger.id
            kwargs['id'] = id
            trigger = self.session.merge(DTrigger(**kwargs))
        else:
            trigger = DTrigger(**kwargs)
        return trigger

    def _get_host(self, hostJson: dict, id) -> DHost:
        kwargs = {
            "name": hostJson.get('name') or 'НЕ ЗАДАНО!',
            "purpose": hostJson.get('role') or 'НЕ ЗАДАНО!',
            "department_owner": hostJson.get('owner.person') or 'НЕ ЗАДАНО!',
            "subsystem": hostJson.get('subsys') or 'НЕ ЗАДАНО!',
            "platform_type": hostJson.get('type') or 'НЕ ЗАДАНО!',
            "os": hostJson.get('os') or 'НЕ ЗАДАНО!',
            "administrator": hostJson.get('owner.person') or 'НЕ ЗАДАНО!',
            "external_id": id
        }
        host = self.session.query(DHost).filter(DHost.external_id == id).one_or_none()
        if host:
            id = host.id
            kwargs['id'] = id
            host = self.session.merge(DHost(**kwargs))
        else:
            host = DHost(**kwargs)
        return host

    def process_channel_data(self, json: dict) -> bool:
        clients = json.get('hosts')
        triggers = json.get('triggers')
        fails = json.get('fails')

        for fail in fails:
            triggerId = fail['triggerid']
            clientId = triggers[triggerId]['hostid']
            failId = fail['events']['begin']
            #trigger = self.make_trigger(triggers[triggerId], int(triggerId))
            client = self._get_client(clients[clientId], int(clientId))
            provider = self._get_provider(clients[clientId])

            dtime_start = datetime.datetime.fromtimestamp(int(fail['period'][0]))
            dtime_end = datetime.datetime.fromtimestamp(int(fail['period'][1]))
            timedelta = (dtime_end - dtime_start).seconds
            sla = 1 if timedelta > 3600 * 4 else 0

            kwargs = {
                "d_client": client,
                "d_provider": provider,
                "event_start_id": failId,
                "id_date_start": dtime_start.date(),
                "id_date_end": dtime_end.date(),
                "id_time_start": tm(dtime_start.time()),
                "id_time_end": tm(dtime_end.time()),
                "id_rfc": 0,
                "id_guilty": 0,
                "id_sla": sla + 1,
                "fact_timedelta": timedelta
            }
            dbFail = self.session.query(FChannelConnect).filter(FChannelConnect.event_start_id == int(failId)).one_or_none()
            if dbFail:
                id = dbFail.id
                kwargs['id'] = id
                dbFail = self.session.merge(FChannelConnect(**kwargs))
            else:
                dbFail = FChannelConnect(**kwargs)
            self.session.add(dbFail)
        try:
            self.session.commit()
            return True
        except Exception as e:
            print(e)
            self.session.rollback()
            return False

    def _get_client(self, clientJson: dict, id) -> DClient:
        kwargs = {
            "full_name": clientJson.get('name') or 'НЕ ЗАДАНО!',
            "org_name": clientJson.get('org') or 'НЕ ЗАДАНО!',
            "address": clientJson.get('addr') or 'НЕ ЗАДАНО!',
            "router_ip": clientJson.get('routerip') or 'НЕ ЗАДАНО!',
            "provider": clientJson.get('prov') or 'НЕ ЗАДАНО!',
            "external_id": id
        }
        client = self.session.query(DClient).filter(DClient.external_id == id).one_or_none()
        if client:
            id = client.id
            kwargs['id'] = id
            client = self.session.merge(DClient(**kwargs))
        else:
            client = DClient(**kwargs)
        return client

    def _get_provider(self, client) -> DProvider:
        provider = self.session.query(DProvider).filter(DProvider.name == client['prov']).one_or_none()
        if provider:
            return provider
        else:
            return DProvider(name=client['prov'])


def tm(t):
    return t.hour * 60 + t.minute

if __name__ == '__main__':
    loader = EtlProcessor()
    file1 = open('../test_data/report001.json')
    json1 = json.load(file1)
    print(loader.process_server_data(json1))
    file2 = open('../test_data/ak.json')
    json2 = json.load(file2)
    print(loader.process_channel_data(json2))