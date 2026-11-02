# the 18 holes, laid out in metres east / north of their area's anchor (areas.py); tee and green are real places
HOLES = [
  dict(name='Times Square', area='ts', par=3, tee=(-35, -40), green=(40, 100)),
  dict(name='Skyline', area='nyroof', par=5, roof=True, direct=True, tee=None, green=None),
  dict(name='Central Park', area='cp', par=4, tee=(62, 515), via=[(50, 330)], green=(25, 152)),
  dict(name='Westminster', area='emb', par=4, tee=(-25, 140), green=(-35, -250)),
  dict(name='Over the Thames', area='tower', par=4, tee=(-45, -150), green=(-20, 205), direct=True),
  dict(name='Bank Job', area='city', par=5, tee=(-300, -45), green=(150, 60), minc=4, wmin=7, margin=3.2),
  dict(name='Champs-Élysées', area='champs', par=4, tee=(179, -92), green=(-120, 48)),
  dict(name='La Tour Eiffel', area='eiffel', par=5, tee=(-230, 250), green=(115, -134), direct=True),
  dict(name='Montmartre', area='mont', par=3, tee=(0, -150), green=(2, 60)),
  dict(name='Shibuya Crossing', area='shibuya', par=5, tee=(128, 484), green=(5, 10)),
  dict(name='Tokyo Tower', area='ttower', par=3, roof=True, direct=True, tee=(-232, 53), green=(-163, 231), roofw=18),
  dict(name='Sensō-ji', area='senso', par=4, tee=(-18, -165), green=(0, 185), minc=2.5, wmin=4.5, margin=2.2),
  dict(name='Dam', area='heren', par=4, tee=(188, 66), green=(211, 453), minc=5, wmin=7, margin=2.5),
  dict(name='Leidseplein', area='ring', par=5, tee=(28, -534), green=(-300, -155), minc=5, wmin=7, margin=2.5),
  dict(name='Museumplein', area='museum', par=3, tee=(110, -90), green=(190, 60)),
  dict(name='Copacabana', area='copa', par=4, tee=(-245, -95), green=(25, 150), minc=6),
  dict(name='Pão de Açúcar', area='urca', par=3, tee=(-420, -420), green=(-330, -600), island=True, nosnap=True),
  dict(name='Jockey Club', area='jockey', par=5, tee=(90, 0), green=(230, 420), minc=6),
]
import math
def _roofline():
    b = math.radians(29); u = (math.sin(b), math.cos(b)); r = (u[1], -u[0]); off = -168
    at = lambda s: (r[0] * off + u[0] * s, r[1] * off + u[1] * s)
    return at(-70), at(372)
HOLES[1]['tee'], HOLES[1]['green'] = _roofline()
