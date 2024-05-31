import ctypes

lib = ctypes.CDLL("libtetris/output/lib/libtetris.so")

class Inputs(ctypes.Structure):
    _fields_ = [('rotate_cw', ctypes.c_bool),
                ('rotate_ccw', ctypes.c_bool),
                ('hold', ctypes.c_bool),
                ('down', ctypes.c_bool),
                ('left', ctypes.c_bool),
                ('right', ctypes.c_bool),
                ('space', ctypes.c_bool)]
    @classmethod
    def from_keys(cls, k: dict):
        return cls(
            rotate_cw = k[0],
            rotate_ccw = k[1],
            hold = k[2],
            down = k[3],
            left = k[4],
            right = k[5],
            space = k[6]
        )
    @classmethod
    def empty(cls):
        return cls(
            rotate_cw = 0,
            rotate_ccw = 0,
            hold = 0,
            down = 0,
            left = 0,
            right = 0,
            space = 0
        )

class Params(ctypes.Structure):
    _fields_ = [('inputs', Inputs),
                ('delta_time', ctypes.c_int)]

    @classmethod
    def from_transaction(cls, t: dict):
        return cls(
            delta_time = t['time'],
            inputs = Inputs.from_keys(t['keys'])
        ) 
    
    @classmethod
    def empty(cls):
        return cls(
            delta_time = 0,
            inputs = Inputs.empty()
        )

class Transaction(ctypes.Structure):
    _fields_ = [('params', Params)]

lib.create_game.restype = ctypes.c_void_p
lib.init.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
lib.tick.argtypes = (ctypes.c_void_p, Params)
lib.destroy_game.argtypes = (ctypes.c_void_p,)
lib.get_lines.argtypes = (ctypes.c_void_p,)
lib.read_game.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
lib.set_seed.argtypes = (ctypes.c_void_p, ctypes.c_int)
lib.run_transactions.argtypes = (ctypes.c_void_p, ctypes.POINTER(Transaction), ctypes.c_int)

class Tetris:
    def __init__(self, seed=0):
        self.handle = lib.create_game()
        lib.set_seed(self.handle, seed)
        lib.init(self.handle, 10, 20, 1000000, 166667, 33000)

    def tick(self, params: Params):
        return lib.tick(self.handle, params)
    
    def __del__(self):
        lib.destroy_game(self.handle)
    
    def print(self):
        lut = [" ", "I", "L", "O", "Z", "T", "J", "S", " ", "_"]
        for y in range(20):
            print("|", end="")
            for x in range(10):
                print(lut[lib.read_game(self.handle, x, y) + 1], end="")
            print("|")
        print("-" * 12)
    
    @property
    def score(self):
        return lib.get_lines(self.handle)

    def run_transactions(self, transactions, length):
        lib.run_transactions(self.handle, transactions, length)