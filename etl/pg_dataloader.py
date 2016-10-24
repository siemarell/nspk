import psycopg2
import etl.config

class Loader:

    def process_json(self, json):
        with psycopg2.connect(etl.config.conn_string) as conn:
            self.process_triggers(json['triggers'],conn)
            self.process_hosts(json['hosts'], conn)
            self.process_fails(json['fails'], conn)
            conn.commit()

    def process_triggers(self, triggers, conn):
        pass

    def process_hosts(self, hosts, conn):
        pass

    def process_fails(self, fails, conn):
        pass