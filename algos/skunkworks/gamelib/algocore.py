import json

from .game_state import GameState
from .util import get_command, debug_write, BANNER_TEXT, send_command

class AlgoCore(object):
    """This class handles communication with the game itself. Your strategy should subclass it.

    Attributes:
        * config (JSON): json object containing information about the game

    """
    def __init__(self):
        self.config = None
        self.jsonState = None

    def on_game_start(self, config):
        """
        Override this to perform initial setup at the start of the game, based
        on the config, a json file which contains information about the game.
        """
        self.config = config
        self.breach_list = []
        self.enemy_spawn_coords = []
        self.enemy_army_cost = 0
        self.enemy_ping_spawn_count = 0
        self.enemy_EMP_spawn_count = 0
        self.army_dict = {'total_count': 0, 'total_cost': 0, 'ping_count': 0, 'EMP_count': 0, 'scrambler_count': 0}
        self.enemy_spawns = []
        self.my_EMP_ids = []
        self.enemy_shield_dict = {}
        self.death_dict = {}
        self.kill_dict = {}
        

    def on_turn(self, game_state):
        """
        This step function is called every turn and is passed a string containing
        the current game state, which can be used to initialize a new GameMap
        """
        self.submit_default_turn()

    def submit_default_turn(self):
        send_command("")
        send_command("")

    # only override this function if you have a 
    def start(self):
        """ 
        Start the parsing loop.
        Python will hang on the readline() statement so actually this program will run forever unless manually stopped or
        it receives the "End" turn message from the game.
        """
        debug_write(BANNER_TEXT)

        while True:
            # Note: Python blocks and hangs on stdin. Can cause issues if connections aren't setup properly and may need to
            # manually kill this Python program.
            game_state_string = get_command()
            if "replaySave" in game_state_string:
                """
                This means this must be the config file. So, load in the config file as a json and add it to your AlgoStrategy class.
                """
                parsed_config = json.loads(game_state_string)
                self.on_game_start(parsed_config)
            elif "turnInfo" in game_state_string:
                state = json.loads(game_state_string)
                self.jsonState = state
                stateType = int(state.get("turnInfo")[0])
                if stateType == 0:
                    """
                    This is the game turn game state message. Algo must now print to stdout 2 lines, one for build phase one for
                    deploy phase. Printing is handled by the provided functions.
                    """
                    self.on_turn(game_state_string)
                elif stateType == 1:
                    """
                    If stateType == 1, this game_state_string string represents the results of an action phase
                    """
                    
                    #for u in state['events']['attack']:
                    #    if u[-2] in self.my_EMP_ids and u[3] == 4:
                    #        debug_write('MY EMP GOT ATTACKED by an EMP!')
                    #        enemyID = u[-3]
                    for u in state['events']['death']:
                        x, y = u[0]
                        unitType = u[1]
                        unitId = u[2]
                        owner = u[3]
                        wasRemoved = u[4]
                        # if it's my stationary unit
                        if owner == 1 and unitType in [0, 1, 2]:
                            if not (x, y) in self.death_dict:
                                self.death_dict[(x, y)] = 1
                            else:
                                self.death_dict[(x, y)] += 1
                        elif owner == 2 and unitType in [3, 4, 5]:
                            if not (x, y) in self.kill_dict:
                                self.kill_dict[(x, y)] = 1
                            else:
                                self.kill_dict[(x, y)] += 1

                    for u in state['events']['spawn']:
                        x, y = u[0]
                        # check if it is an enemy spawn attacking unit (PING, EMP, SCRAMBLER)
                        if u[1] in [3,4,5] and y > 13:
                            self.army_dict["total_count"] += 1
                            self.enemy_spawns.append(u)
                            if u[1] == 3:
                                self.enemy_ping_spawn_count += 1
                                self.army_dict["total_cost"] += 1
                                self.army_dict["ping_count"] += 1
                            elif u[1] == 4:
                                self.enemy_EMP_spawn_count += 1
                                self.army_dict["total_cost"] += 3
                                self.army_dict["EMP_count"] += 1
                            elif [1] == 5:
                                self.army_dict["total_cost"] += 1
                                self.army_dict["scrambler_count"] += 1

                            if u[0] not in self.enemy_spawn_coords:
                                self.enemy_spawn_coords.append(u[0])
                                debug_write('SPAWN at {}'.format(u[0]))

                    for u in state['events']['breach']:
                        x, y = u[0]
                        #debug_write('breach - {}'.format(u))
                        if y < 14:
                            if u[0] not in self.breach_list:
                                # make sure it wasn't my breach!!!
                                self.breach_list.append(u[0])
                    #debug_write('breachList - {}'.format(self.breach_list))

                    continue
                elif stateType == 2:
                    """
                    This is the end game message. This means the game is over so break and finish the program.
                    """
                    debug_write("Got end state quitting bot.")
                    break
                else:
                    """
                    Something is wrong? Recieved an incorrect or imporperly formatted string.
                    """
                    debug_write("Got unexpected string with turnInfo: {}".format(game_state_string))
            else:
                """
                Something is wrong? Recieved an incorrect or imporperly formatted string.
                """
                debug_write("Got unexpected string : {}".format(game_state_string))
