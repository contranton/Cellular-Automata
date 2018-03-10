"""
Define Base Cell class

"""

import re

from collections import defaultdict


class CellConfig:
    """Define possible states and ruleset"""

    def __init__(self):
        # Labeled num-label pairs
        #
        # Example:
        # {0: "Dead", 1: "Alive", 2:"Infected"}
        self._possible_states = {}
        self._rules = {}
        self._switching_rules = {}

    @property
    def possible_states(self):
        """Return list of possible numerical states for a cell"""
        return tuple(self._possible_states.keys())

    @possible_states.setter
    def possible_states(self, state_dict):
        if not self.__validate_states(state_dict):
            print("Invalid State Dict. System unchanged.")
        else:
            self._possible_states = state_dict

    @possible_states.deleter
    def possible_states(self):
        self._possible_states = {}

    @property
    def rules(self):
        """
        Tuple with state-change rules A 4-tuple (rule) defines, for
        each state [0], the number of neighbors [2] of some state
        [1] so that the cell changes to the specified state [3].

        In the case of conflicts, i.e. when a cell surrounded by 2
        cells of different states has a rule for both of these
        cases, the behavior is governed by the ALLOW_CONFLICTS
        flag. When True, one of the possible results is chosen
        randomly. Otherwise, a RuleConflictException is thrown and
        states and rules with relatively large numbers until a more
        the rule is deemed invalid. To avoid this, begin with a few
        robust rule system is in place.

        Example:
        Game of life:
        "0:1(234)1,1:1(5678)0" becomes:
        {0:{1: ({2,3,4}, 1)}, 1: {1: ({5,6,7,8}, 0)}}
        And means:
        Initial state 0, when faced with 2,3 or 4 neighbors, becomes state 1,
         and initial state 1, when faced with 5,6,7, or 8 neighbors, becomes 0
        """
        return self._rules

    @rules.setter
    def rules(self, rulestring):
        if not self.__validate_rulestring(rulestring):
            print("Invalid Ruleset tuple. System Unchanged")
            raise Exception("Invalid Rule")
        else:
            self._rules = self.__parse_rulestring(rulestring)

    @rules.deleter
    def rules(self):
        self._rules = ()

    @property
    def switching_rules(self):
        return self._switching_rules

    @switching_rules.setter
    def switching_rules(self, rulestring):
        if not self.__validate_switching_rulestring(rulestring):
            raise Exception("Invalid Switching Rule")
        else:
            self._switching_rules = self.__parse_switching_rulestring(
                rulestring)

    def __get_possible_states_string(self):
        """
        Returns a string containing the states defined in the config in
        the form '[123]' for a config with those 3 states.  To be used
        with the rule validators
        """
        s_ = "".join(["%d"]*len(self.possible_states)) % self.possible_states
        s_ = "[%s]" % s_
        return s_

    def __validate_states(self, state_dict):
        """Ensures state-dict follows the 'int: String' format"""
        for key in state_dict.keys():
            if type(key) is not int:
                return False

        for val in state_dict.values():
            if type(val) is not str:
                return False

        return True

    def __validate_rulestring(self, rulestring):
        """Ensures rule-set follows valid format and that it uses the states
        previously defined.

        TODO: Check for collisions

        """
        rules = rulestring.split(",")

        # Make sure only states defined in possible_states are used
        s_ = self.__get_possible_states_string()
        r = re.compile('{0}:{0}\([0-8]*\){0}'.format(s_))
        if any([r.match(i) is None for i in rules]):
            return False
        return True

    def __validate_switching_rulestring(self, rulestring):
        rules = rulestring.split(",")

        s_ = self.__get_possible_states_string()
        r = re.compile('{0}:{0}\(\d\.\d+\)'.format(s_))

        # Check for format
        if any([r.match(i) is None for i in rules]):
            return False

        # Check that p <= 1.0
        probs = [float(i[i.find("(") + 1: i.find(")")]) for i in rules]
        if any([p > 1.0 for p in probs]):
            print("Invalid Probability")
            return False

        return True

    def __parse_rulestring(self, rulestring):
        ruleset = {}
        rules = rulestring.split(",")
        for r in rules:
            init_state = int(r[0])
            neighb_state = int(r[2])
            final_state = int(r[-1])
            counts = r[r.find("(") + 1:r.find(")")]
            counts = [int(i) for i in counts]

            if init_state not in ruleset:
                ruleset[init_state] = {
                    neighb_state: (set(counts), final_state)}
            else:
                ruleset[init_state][neighb_state] = (set(counts), final_state)

        return ruleset

    def __parse_switching_rulestring(self, rulestring):
        sw_ruleset = {}
        rules = rulestring.split(",")
        for r in rules:
            init_state = int(r[0])
            final_state = int(r[2])
            probability = float(r[r.find("(") + 1:r.find(")")])

            sw_ruleset[init_state] = (final_state, probability)
        return sw_ruleset


class Cell():
    """
    Stores position and state
    """

    def __init__(self, state, coords):
        self._state = None
        self.current_state = state
        self.coords = coords

        self.is_edge = False

        self.neighbors = defaultdict(int)

    @property
    def current_state(self):
        """Cell state, managed by Board and CellConfig classes"""
        return self._state

    @current_state.setter
    def current_state(self, state):
        self._state = state

    def reset_neighbors(self):
        for i in self.neighbors:
            self.neighbors[i] = 0
