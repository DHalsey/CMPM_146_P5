import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf, ceil
from random import choice

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

make_tools = {'craft bench': 'bench', 'craft furnace at bench': 'furnace', 'craft iron_axe at bench': 'iron_axe', 'craft iron_pickaxe at bench': 'iron_pickaxe', 'craft stone_axe at bench': 'stone_axe', 'craft stone_pickaxe at bench': 'stone_pickaxe', 'craft wooden_axe at bench': 'wooden_axe', 'craft wooden_pickaxe at bench': 'wooden_pickaxe'}

class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    hasRequirements = 'Requires' in rule.keys()
    ConsumesItems = 'Consumes' in rule.keys()

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if ConsumesItems:
            for item in rule['Consumes']:
                if state[item] < rule['Consumes'][item]:
                    return False
        if hasRequirements:
            for item in rule['Requires']:
                if state[item] < 1:
                    return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    ConsumesItems = 'Consumes' in rule.keys() 

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        for item in rule['Produces']:
            next_state[item] = state[item] + rule['Produces'][item]

        if ConsumesItems:
            for item in rule['Consumes']:
                next_state[item] = state[item] - rule['Consumes'][item]

        next_state['Time'] += rule['Time']

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for item in goal:
            if state[item] < goal[item]:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)

def make_heuristic(goal, recipes):
    total_items = 0
    total_resource_cost = {}
    items_to_parse = []
    tool_req = {}
    for keys in goal.keys():
        items_to_parse.append([keys, goal[keys]]);
        total_resource_cost[keys] = goal[keys]
        total_items += goal[keys]

    while items_to_parse:
        item,amount = items_to_parse.pop(0)
        temp_worst_item = 0
        temp_worst_time = 0
        for name, r in recipes.items():
            if item in r['Produces']:
                min_makeable = r['Produces'][item] #the minimum of the item that can be made (IE 4 planks)
                if 'Requires' in r:
                    for item2 in r['Requires']:
                        if r['Time'] > temp_worst_time:
                            temp_worst_time = r['Time']
                            temp_worst_item = item2
                if 'Consumes' in r:
                    for item2 in r['Consumes']:
                        if(item2 in total_resource_cost): #combine totals if it already exists
                            numToMake = r['Consumes'][item2]*amount/r['Produces'][item]
                            total_resource_cost[item2] += numToMake #add in consumables to dict for the number needed
                            total_items+=numToMake
                            items_to_parse.append([item2, numToMake])
                        else:
                            numToMake = r['Consumes'][item2]*amount/r['Produces'][item]
                            total_resource_cost[item2] = numToMake #create the new item if it didnt exist
                            total_items+=numToMake
                            items_to_parse.append([item2, numToMake])
        if temp_worst_time > 0 and temp_worst_item not in tool_req:
            total_resource_cost[temp_worst_item] = 1
            total_items+=1
            items_to_parse.append([temp_worst_item,1])
            tool_req[temp_worst_item] = 1

    #while items_to_parse: #loop while we still need to parse more items
    
    
    #while len(breakdown_items_dict) > 0:



    def heuristic(state, action):
        # Implement your heuristic here!
        temp_state = action.effect(state)
        state_cost = {}
        state_parse = []
        state_tool_req = {}
        #list_of_tools = {'bench','wooden_pickaxe','stone_pickaxe','iron_pickaxe','wooden_axe','stone_axe','iron_axe','furnace'}

        for keys in temp_state.keys():
            if temp_state[keys] > 0 and keys is not 'Time':
                state_parse.append([keys, temp_state[keys]])
                state_cost[keys] = temp_state[keys]

        while state_parse:
            item,amount = state_parse.pop(0)
            temp_worst_item = 0
            temp_worst_time = 0
            for name, r in recipes.items():
                if item in r['Produces']:
                    min_makeable = r['Produces'][item] #the minimum of the item that can be made (IE 4 planks)
                    """if 'Requires' in r:
                        for item2 in r['Requires']:
                            if r['Time'] > temp_worst_time:
                                temp_worst_time = r['Time']
                                temp_worst_item = item2"""
                    if 'Consumes' in r:
                        for item2 in r['Consumes']:
                            if(item2 in state_cost): #combine totals if it already exists
                                numToMake = r['Consumes'][item2]*amount/r['Produces'][item]
                                state_cost[item2] += numToMake #add in consumables to dict for the number needed
                                state_parse.append([item2, numToMake])
                            else:
                                numToMake = r['Consumes'][item2]*amount/r['Produces'][item]
                                state_cost[item2] = numToMake #create the new item if it didnt exist
                                state_parse.append([item2, numToMake])
            if temp_worst_time > 0 and temp_worst_item not in state_tool_req:
                state_cost[temp_worst_item] = 1
                state_parse.append([temp_worst_item,1])
                state_tool_req[temp_worst_item] = 1


        """print("TOTAL COST GOAL: " , total_resource_cost)
        print("PARSE ITEMS GOAL: " , items_to_parse,)
        print("TOTAL COST STATE: " , state_cost)
        print("PARSE ITEMS STATE: " , state_parse,"\n")
        print()"""
        heuristic_cost = total_items
        for key_state in state_cost.keys():
            if key_state in total_resource_cost.keys():
                difference = total_resource_cost[key_state] - state_cost[key_state]
                if difference >= 0:
                    heuristic_cost -= state_cost[key_state]
                else:
                    heuristic_cost -= total_resource_cost[key_state]
        return heuristic_cost*5
    return heuristic



def search(graph, state, is_state, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    
    #A* search of action space

    # initialize empty queue
    queue = []

    # initialize empty dictionary of backpointers
    backpointers = {}

    # set of visited states
    visited = set()

    # add source to queue
    heappush(queue, (0, 0, state, None))

    #mark source as visited
    test_state = state.copy()
    test_state['Time'] = 0
    visited.add(test_state)

    while time() - start_time < limit:
        # expand node if queue is non-empty
        if queue:
            # get current node with cost
            current_priority, current_cost, current_state, parent_action = heappop(queue)

            #print(current_state) #DEBUG TO SHOW OUTPUT

            # construct and return path when goal is reached
            if is_goal(current_state):
                # initialize path (state, action)
                path = []

                # initialize temp state and action
                temp_state = current_state
                temp_action = parent_action

                # append goal action state
                path.insert(0, (temp_state, temp_action))

                # construct path from backpointers
                if temp_action is None:
                    print(time(), " seconds")
                    print(0, " steps")
                    return path

                while backpointers[(temp_state, temp_action)][1] is not None:
                    temp_state, temp_action = backpointers[(temp_state, temp_action)]
                    path.insert(0, (temp_state, temp_action.name))

                print(time(), " seconds")
                print(len(path), " steps")

                return path

            # expand current state with all valid actions
            for r in all_recipes:
                if r.check(current_state):
    
                    # get next state given action r
                    new_state = r.effect(current_state)
                    test_state = new_state.copy()
                    test_state['Time'] = 0
                    if test_state not in visited:
                        # get cost of action r
                        cost = current_cost + r.cost

                        # get priority with heuristic
                        priority = cost + heuristic(current_state, r)

                        # push next state with parent action
                        heappush(queue, (priority, cost, new_state, r))

                        # set backpointer
                        backpointers[(new_state, r)] = (current_state, parent_action)

                        # set test_state as visited
                        visited.add(test_state) 
        pass

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state['Time'] = 0
    state.update(Crafting['Initial'])

    # generate hueristic
    heuristic = make_heuristic(Crafting['Goal'], Crafting['Recipes'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
