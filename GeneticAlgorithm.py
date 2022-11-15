from OptimisationAlgorithm import OptimisationAlgorithm

class GeneticAlgorithm(OptimisationAlgorithm):
    def __init__(self, iterations, simulation_length, **kwargs):
        super().__init__(iterations, simulation_length)
        
