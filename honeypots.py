import asyncio
from core.proto.telnet import telnetProtocol
from core.proto.mysql import mysqlProtocol


# 启动服务器 #
try:
    async def main():
        loop = asyncio.get_running_loop()

        async def run_service(proto,port):
            server = await loop.create_server(proto, '0.0.0.0', port)
            await server.serve_forever()

        allroco_tasks = []

        allroco_tasks.append(run_service(mysqlProtocol, 3306))
        allroco_tasks.append(run_service(telnetProtocol, 23))

        await asyncio.gather(*allroco_tasks)

    asyncio.run(main())

except:
    # old version
    loop = asyncio.get_event_loop()
    allroco_tasks = []

    allroco_tasks.append(loop.create_server(mysqlProtocol, "0.0.0.0", 3306))
    allroco_tasks.append(loop.create_server(telnetProtocol, "0.0.0.0", 23))

    server = loop.run_until_complete(asyncio.gather(*allroco_tasks))
    loop.run_forever()