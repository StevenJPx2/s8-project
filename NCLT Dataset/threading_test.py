import asyncio
from time import perf_counter


async def sleep(sleep_time):
    process = await asyncio.create_subprocess_shell(f"sleep {sleep_time}")
    await process.wait()


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=None, stderr=None)

    await proc.wait()


async def gather_cmds(fn, *args, **kwargs):
    await asyncio.gather(*[fn(*args, **kwargs)] * 100)


st_ti = perf_counter()

asyncio.run(
    gather_cmds(run, "curl https://www.youtube.com/watch\?v\=GB2gnayGlkI\&t\=361s")
)

print(perf_counter() - st_ti)
