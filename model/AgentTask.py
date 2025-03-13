import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AgentTask(Base):
    __tablename__ = 'agent_task'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    taskName = Column('task_name',String(64), nullable=False)
    taskCron = Column('task_cron',String(64), nullable=False)
    taskContent = Column('task_content',String(512), nullable=False)
    createTime = Column('create_time',DateTime, default=datetime.datetime.utcnow)
