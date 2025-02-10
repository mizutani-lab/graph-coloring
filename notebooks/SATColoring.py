import time

from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, ITotalizer
from pysat.solvers import Solver
from pysat.solvers import Glucose4 as Glucose


try:
    from pysat.solvers import Cadical153 as Cadical  # v0.1.8-
except ImportError:
    from pysat.solvers import Cadical
import networkx as nx


class SATColoring:
    def __init__(self, G: nx.Graph, solver: Solver = Cadical):
        self.G = G

        self.solution = None
        self.chromatic_number = None
        self.solver = solver

    def solve(self):
        # Handle special cases.
        if self.G.number_of_nodes() == 0:
            # no vertices
            self.solution = {}
            self.chromatic_number = 0
            return
        if self.G.number_of_edges() == 0:
            # no edges
            self.solution = {v: 0 for v in self.G}
            self.chromatic_number = 1
            return
        if nx.is_bipartite(self.G):
            # 2-colorable
            self.solution = nx.bipartite.color(self.G)
            self.chromatic_number = 2
            return

        # General case.
        obj = 3

        while True:
            # Create CNF.
            vpool = IDPool(start_from=1)
            cnf = CNF()

            # Each vertex has at least one color.
            for v in self.G:
                cnf.append([vpool.id(f'x_{c}_{v}') for c in range(obj)])

                # Sometimes stronger constraints help.
                # cnf.extend(CardEnc.equals([vpool.id(f'x_{c}_{v}') for c in range(obj)], vpool=vpool))

            # Adjacent vertices cannot be colored using the same color.
            for u, v in self.G.edges():
                for c in range(obj):
                    cnf.append([-vpool.id(f'x_{c}_{u}'), -vpool.id(f'x_{c}_{v}')])

            # Run solver.
            with self.solver() as s:
                s.append_formula(cnf)

                solve_start = time.time()
                print(f'Solving: objective={obj}, solver={self.solver.__name__}')
                ret = s.solve(assumptions=[])
                print(f'Solved : objective={obj}, ret={ret}, elapsed={time.time() - solve_start:.3f}s')
                if ret:
                    # decode result
                    model = {abs(x): x > 0 for x in s.get_model()}
                    solution = {}
                    for v in self.G:
                        for c in range(obj):
                            if model[vpool.id(f'x_{c}_{v}')]:
                                solution[v] = c
                                break
                    self.solution = solution
                    self.chromatic_number = obj
                    break

            # Increment the objective.
            obj += 1
