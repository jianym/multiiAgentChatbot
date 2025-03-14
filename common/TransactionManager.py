from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextvars import ContextVar
import config

# 数据库配置
DATABASE_URL = config.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 上下文变量用于管理嵌套事务中的会话
session_context: ContextVar = ContextVar("session_context", default=None)

# 事务传播类型
class Propagation:
    REQUIRED = "REQUIRED"  # 如果存在事务，就复用；没有就创建新事务（默认行为）
    REQUIRES_NEW = "REQUIRES_NEW"  # 总是新开一个事务，独立提交和回滚

# 事务管理装饰器
def transactional(propagation=Propagation.REQUIRED):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_session = session_context.get()

            # REQUIRED：复用当前事务（如果有）
            if propagation == Propagation.REQUIRED and isinstance(current_session, AsyncSession):
                return await func(current_session, *args, **kwargs)

            # REQUIRES_NEW：总是创建新事务
            session = SessionLocal()
            token = session_context.set(session)

            try:
                result = await func(session=session, *args, **kwargs)
                await session.commit()  # 异步提交
                return result
            except Exception as e:
                await session.rollback()  # 异步回滚
                print(f"事务回滚，原因：{e}")
                raise
            finally:
                await session.close()
                session_context.reset(token)

        return wrapper
    return decorator