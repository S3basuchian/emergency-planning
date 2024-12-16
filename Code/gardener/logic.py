import clingo
from clingo import Number, Function
from utils import get_current_time_ms


class Logic:
    def __init__(self, instance, learning, horizon, radius):
        self.instance = instance
        self.learning = learning
        self.radius = radius
        self.horizon = horizon
        self.time_diff = []
        self.ctl = None
        self.cache = []

    def on_model(self, m):
        self.save_solution(m)
        show = " ".join([str(i) for i in m.symbols(shown=True)])
        #print("Answer:\n{}".format(show))

    def save_solution(self, m):
        self.player = []
        self.final = False
        for sym in m.symbols(shown=True):
            match sym.name:
                case "action_taken":
                    if len(sym.arguments) == 4:
                        while len(self.player) < sym.arguments[1].number + 1:
                            self.player.append(0)
                        self.player[sym.arguments[1].number] = sym.arguments[
                            0].number

    def setup(self):
        self.max_frogs = min(pow((self.radius * 2 + 1), 2) - 1,
                             len(self.instance.frogs))
        self.ctl = clingo.Control(["-c", f"horizon={self.horizon}", "-c",
                                   f"frogs={self.max_frogs}", "-c",
                                   f"radius={self.radius}", "-c",
                                   f"size={self.instance.size}"])
        self.ctl.load('program.lp')
        self.ctl.ground([("base", [])], context=self)

    def reset_clingo_externals(self):
        for i in range(1, 11):
            self.ctl.assign_external(Function("multi", [
                Number(i)
            ]), False)
        for i in range(1, self.instance.size + 1):
            for j in range(1, self.instance.size + 1):
                self.ctl.assign_external(Function("player", [
                    Number(i),
                    Number(j)
                ]), False)
        for c, f in enumerate(self.instance.frogs):
            self.ctl.assign_external(Function("foutside", [
                Number(c)
            ]), False)
        for i in range(self.radius + 1):
            for c, f in enumerate(self.instance.frogs):
                self.ctl.assign_external(Function("fcol", [
                    Number(c),
                    Number(i),
                    Number(0)
                ]), False)
                self.ctl.assign_external(Function("fcol", [
                    Number(c),
                    Number(-i),
                    Number(0)
                ]), False)
                self.ctl.assign_external(Function("frow", [
                    Number(c),
                    Number(i),
                    Number(0)
                ]), False)
                self.ctl.assign_external(Function("frow", [
                    Number(c),
                    Number(-i),
                    Number(0)
                ]), False)
            for j in range(self.radius + 1):
                self.ctl.assign_external(Function("wall", [
                    Number(i),
                    Number(j)
                ]), False)
                self.ctl.assign_external(Function("wall", [
                    Number(-i),
                    Number(j)
                ]), False)
                self.ctl.assign_external(Function("wall", [
                    Number(i),
                    Number(-j)
                ]), False)
                self.ctl.assign_external(Function("wall", [
                    Number(-i),
                    Number(-j)
                ]), False)
            for j in range(self.radius + 1):
                self.ctl.assign_external(Function("plant", [
                    Number(i),
                    Number(j)
                ]), False)
                self.ctl.assign_external(Function("plant", [
                    Number(-i),
                    Number(j)
                ]), False)
                self.ctl.assign_external(Function("plant", [
                    Number(i),
                    Number(-j)
                ]), False)
                self.ctl.assign_external(Function("plant", [
                    Number(-i),
                    Number(-j)
                ]), False)
            for j in range(self.radius + 1):
                self.ctl.assign_external(Function("target", [
                    Number(i),
                    Number(j)
                ]), False)
                self.ctl.assign_external(Function("target", [
                    Number(-i),
                    Number(j)
                ]), False)
                self.ctl.assign_external(Function("target", [
                    Number(i),
                    Number(-j)
                ]), False)
                self.ctl.assign_external(Function("target", [
                    Number(-i),
                    Number(-j)
                ]), False)
            for j in range(self.radius + 1):
                for a in range(4):
                    for r in range(4):
                        self.ctl.assign_external(Function("action", [
                            Number(a),
                            Number(r),
                            Number(i),
                            Number(j)
                        ]), False)
                        self.ctl.assign_external(Function("action", [
                            Number(a),
                            Number(r),
                            Number(-i),
                            Number(j)
                        ]), False)
                        self.ctl.assign_external(Function("action", [
                            Number(a),
                            Number(r),
                            Number(i),
                            Number(-j)
                        ]), False)
                        self.ctl.assign_external(Function("action", [
                            Number(a),
                            Number(r),
                            Number(-i),
                            Number(-j)
                        ]), False)

    def set_clingo_externals(self):
        midpoint = self.instance.player

        # player
        self.ctl.assign_external(
            Function("player", [Number(midpoint[0]),
                                Number(midpoint[1])]), True)

        multi = self.instance.visited[midpoint]
        self.ctl.assign_external(Function("multi", [
            Number(multi)
        ]), True)

        # walls & plants
        for i in range(self.radius + 1):
            for j in range(self.radius + 1):
                absolut = (midpoint[0] + i, midpoint[1] + j)
                for a in range(4):
                    r = self.learning.get_action_rank((absolut[0], absolut[1]),
                                                      a)
                    self.ctl.assign_external(Function("action", [
                        Number(a),
                        Number(r),
                        Number(i),
                        Number(j)
                    ]), True)
                if absolut == self.instance.target:
                    self.ctl.assign_external(
                        Function("target", [Number(i), Number(j)]), True)
                if absolut in self.instance.plants and absolut not in self.instance.dead_plants:
                    self.ctl.assign_external(
                        Function("plant", [Number(i), Number(j)]), True)
                if absolut in self.instance.walls:
                    self.ctl.assign_external(
                        Function("wall", [Number(i), Number(j)]), True)
                if absolut[0] < 1 or absolut[1] < 1 or absolut[
                    0] > self.instance.size or absolut[
                    1] > self.instance.size:
                    self.ctl.assign_external(
                        Function("wall", [Number(i), Number(j)]), True)

                absolut = (midpoint[0] - i, midpoint[1] + j)
                for a in range(4):
                    r = self.learning.get_action_rank((absolut[0], absolut[1]),
                                                      a)
                    self.ctl.assign_external(Function("action", [
                        Number(a),
                        Number(r),
                        Number(-i),
                        Number(j)
                    ]), True)
                if absolut == self.instance.target:
                    self.ctl.assign_external(
                        Function("target", [Number(-i), Number(j)]), True)
                if absolut in self.instance.plants and absolut not in self.instance.dead_plants:
                    self.ctl.assign_external(
                        Function("plant", [Number(-i), Number(j)]), True)
                if absolut in self.instance.walls:
                    self.ctl.assign_external(
                        Function("wall", [Number(-i), Number(j)]), True)
                if absolut[0] < 1 or absolut[1] < 1 or absolut[
                    0] > self.instance.size or absolut[
                    1] > self.instance.size:
                    self.ctl.assign_external(
                        Function("wall", [Number(-i), Number(j)]), True)

                absolut = (midpoint[0] + i, midpoint[1] - j)
                for a in range(4):
                    r = self.learning.get_action_rank((absolut[0], absolut[1]),
                                                      a)
                    self.ctl.assign_external(Function("action", [
                        Number(a),
                        Number(r),
                        Number(i),
                        Number(-j)
                    ]), True)
                if absolut == self.instance.target:
                    self.ctl.assign_external(
                        Function("target", [Number(i), Number(-j)]), True)
                if absolut in self.instance.plants and absolut not in self.instance.dead_plants:
                    self.ctl.assign_external(
                        Function("plant", [Number(i), Number(-j)]), True)
                if absolut in self.instance.walls:
                    self.ctl.assign_external(
                        Function("wall", [Number(i), Number(-j)]), True)
                if absolut[0] < 1 or absolut[1] < 1 or absolut[
                    0] > self.instance.size or absolut[
                    1] > self.instance.size:
                    self.ctl.assign_external(
                        Function("wall", [Number(i), Number(-j)]), True)

                absolut = (midpoint[0] - i, midpoint[1] - j)
                for a in range(4):
                    r = self.learning.get_action_rank((absolut[0], absolut[1]),
                                                      a)
                    self.ctl.assign_external(Function("action", [
                        Number(a),
                        Number(r),
                        Number(-i),
                        Number(-j)
                    ]), True)
                if absolut == self.instance.target:
                    self.ctl.assign_external(
                        Function("target", [Number(-i), Number(-j)]), True)
                if absolut in self.instance.plants and absolut not in self.instance.dead_plants:
                    self.ctl.assign_external(
                        Function("plant", [Number(-i), Number(-j)]), True)
                if absolut in self.instance.walls:
                    self.ctl.assign_external(
                        Function("wall", [Number(-i), Number(-j)]), True)
                if absolut[0] < 1 or absolut[1] < 1 or absolut[
                    0] > self.instance.size or absolut[
                    1] > self.instance.size:
                    self.ctl.assign_external(
                        Function("wall", [Number(-i), Number(-j)]), True)

        # frogs
        count_frog = 0
        for c, f in enumerate(self.instance.frogs):
            relative = (f[0] - midpoint[0], f[1] - midpoint[1])
            if abs(relative[0]) > self.radius or abs(
                    relative[
                        1]) > self.radius or f in self.instance.dead_frogs:
                #    self.ctl.assign_external(Function("foutside", [Number(c)]),
                #                             True)
                pass
            else:
                self.ctl.assign_external(
                    Function("fcol",
                             [Number(count_frog), Number(relative[0]),
                              Number(0)]),
                    True)
                self.ctl.assign_external(
                    Function("frow",
                             [Number(count_frog), Number(relative[1]),
                              Number(0)]),
                    True)
                count_frog += 1
        for i in range(count_frog, self.max_frogs):
            self.ctl.assign_external(Function("foutside", [Number(i)]),
                                     True)

    def get_action(self, cache):

        time_pre_compute = get_current_time_ms()

        # Failsafe: If the framework is stuck in a loop, follow the RL
        if self.instance.visited[self.instance.player] > 10:
            self.cache.clear()
            return self.learning.get_action(self.instance)

        # If there are any cached actions use them fist
        if len(self.cache) > 0:
            action = self.cache.pop(0)
            time_post_compute = get_current_time_ms()
            time_diff = time_post_compute - time_pre_compute
            self.time_diff.append(time_diff)
            return action

        self.player = []

        # Reset the clingo window
        self.reset_clingo_externals()

        # Set all externals of the currently considered window (see section
        # "Optimization-> Windowing" in the main document for more information)
        # Externals include cell information (walls, frogs, plants) as well as
        # information about policy preferences
        self.set_clingo_externals()

        # solve the LP
        self.ctl.solve(on_model=self.on_model)

        # measure the computation time
        time_post_compute = get_current_time_ms()
        time_diff = time_post_compute - time_pre_compute
        self.time_diff.append(time_diff)

        # cache further actions if desired and return current next action
        action = self.player[0]
        if cache > 1:
            for i in range(1, cache):
                rel = self.player[i]
                self.cache.append(rel)
        return action

    def get_reward(self, a, c, r):
        rank = self.learning.get_action_rank((c.number, r.number), a.number)
        return Number(rank)
