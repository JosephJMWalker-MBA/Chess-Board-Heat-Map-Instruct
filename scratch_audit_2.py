import sys
sys.path.append('src')
import chessheat.cp_instrument as cpi
import inspect
print(inspect.getsource(cpi.InstrumentSession.start))
print(inspect.getsource(cpi.InstrumentSession.acquire))
