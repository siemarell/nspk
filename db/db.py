# coding: utf-8
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Calendar(Base):
    __tablename__ = 'calendar'

    date = Column(Date, primary_key=True)
    year = Column(Integer)
    halfyear = Column(Integer)
    quarter = Column(Integer)
    month_number = Column(Integer)
    month = Column(Text)
    day = Column(Integer)
    week_number = Column(Integer)
    week_day = Column(Text)
    day_number = Column(Integer)


class DClient(Base):
    __tablename__ = 'd_client'

    id = Column(Integer, primary_key=True, server_default=text("nextval('d_client_id_seq'::regclass)"))
    name = Column(Text)


class DGuilty(Base):
    __tablename__ = 'd_guilty'

    id = Column(Integer, primary_key=True, server_default=text("nextval('d_guilty_id_seq'::regclass)"))
    name = Column(Text)


class DHost(Base):
    __tablename__ = 'd_host'

    id = Column(Integer, primary_key=True, server_default=text("nextval('d_host_id_seq'::regclass)"))
    name = Column(String)
    purpose = Column(Text)
    division_owner = Column(Text)
    subsystem = Column(Text)
    platform_type = Column(Text)
    os = Column(Text)
    administrator = Column(Text)
    external_id = Column(Integer)


class DProvider(Base):
    __tablename__ = 'd_provider'

    id = Column(Integer, primary_key=True, server_default=text("nextval('d_provider_id_seq'::regclass)"))
    name = Column(Text)


class DRfc(Base):
    __tablename__ = 'd_rfc'

    id = Column(Integer, primary_key=True, server_default=text("nextval('d_rfc_id_seq'::regclass)"))
    name = Column(Text)


class DTime(Base):
    __tablename__ = 'd_time'

    id = Column(Integer, primary_key=True)
    time_text = Column(String)
    hour = Column(Integer)
    quarterhour = Column(String)
    minute = Column(Integer)
    daytimename = Column(String)
    daynight = Column(String)


class DTrigger(Base):
    __tablename__ = 'd_trigger'

    id = Column(Integer, primary_key=True, server_default=text("nextval('d_trigger_id_seq'::regclass)"))
    name = Column(String)
    source_name = Column(String)
    external_id = Column(Integer)


class FChannelConnect(Base):
    __tablename__ = 'f_channel_connect'

    id = Column(Integer, primary_key=True)
    id_date_start = Column(ForeignKey('calendar.date'), index=True)
    id_date_end = Column(ForeignKey('calendar.date'), index=True)
    id_client = Column(ForeignKey('d_client.id'), index=True)
    id_provider = Column(ForeignKey('d_provider.id'), index=True)
    id_rfc = Column(ForeignKey('d_rfc.id'), index=True)
    id_guilty = Column(ForeignKey('d_guilty.id'), index=True)
    fact_timedelta = Column(Integer)
    fact_sla = Column(Integer)
    id_time_start = Column(ForeignKey('d_time.id'), index=True)
    id_time_end = Column(ForeignKey('d_time.id'), index=True)

    d_client = relationship('DClient')
    calendar = relationship('Calendar', primaryjoin='FChannelConnect.id_date_end == Calendar.date')
    calendar1 = relationship('Calendar', primaryjoin='FChannelConnect.id_date_start == Calendar.date')
    d_guilty = relationship('DGuilty')
    d_provider = relationship('DProvider')
    d_rfc = relationship('DRfc')
    d_time = relationship('DTime', primaryjoin='FChannelConnect.id_time_end == DTime.id')
    d_time1 = relationship('DTime', primaryjoin='FChannelConnect.id_time_start == DTime.id')


class FServIncident(Base):
    __tablename__ = 'f_serv_incident'

    id = Column(Integer, primary_key=True, server_default=text("nextval('f_serv_incident_id_seq'::regclass)"))
    id_host = Column(ForeignKey('d_host.id'), index=True)
    id_date_start = Column(ForeignKey('calendar.date'), index=True)
    id_date_end = Column(ForeignKey('calendar.date'), index=True)
    id_trigger = Column(ForeignKey('d_trigger.id'), index=True)
    fact_timedelta = Column(Integer)
    id_time_start = Column(ForeignKey('d_time.id'), index=True)
    id_time_end = Column(ForeignKey('d_time.id'), index=True)

    calendar = relationship('Calendar', primaryjoin='FServIncident.id_date_end == Calendar.date')
    calendar1 = relationship('Calendar', primaryjoin='FServIncident.id_date_start == Calendar.date')
    d_host = relationship('DHost')
    d_time = relationship('DTime', primaryjoin='FServIncident.id_time_end == DTime.id')
    d_time1 = relationship('DTime', primaryjoin='FServIncident.id_time_start == DTime.id')
    d_trigger = relationship('DTrigger')