// ***************************************************
// An example of Evolving CTRNN controllers for Walkers
// ***************************************************

#include "TSearch.h"


const double RunDuration = 250;
const double StepSize = 0.01;

//Evaluate the performance of CTRNN controllers with walkers
double Evaluate(TVector<double> &v, RandomState &)
{

	//Create a CTRNN from the vector passed in
	CTRNN c(2);
    c.SetNeuronBias(1, v[1] );
    c.SetNeuronBias(2, v[2] );
    c.SetConnectionWeight(1, 1, v[3] );
    c.SetConnectionWeight(1, 2, v[4] );
    c.SetConnectionWeight(2, 1, v[5] );
    c.SetConnectionWeight(2, 2, v[6] ;

    // Run the circuit
    c.RandomizeCircuitState(-0.5,0.5);
    //cout << 0.0 << " " << c.NeuronOutput(1) << " " << c.NeuronOutput(2) << endl;
    //for (double time = StepSize; time <= RunDuration; time += StepSize) {
    //    c.EulerStep(StepSize);
    //    cout << time << " " << c.NeuronOutput(1) << " " << c.NeuronOutput(2) << endl;
    //}



	//Create a One Legged Walker from the CTRNN
	LeggedAgent Insect;
	Insect.NervousSystem = c;

    // Run the agent
    SetRandomSeed(RandomSeed);
    Insect.Reset(0, 0, 0);

    for (double time = 0; time < RunDuration; time += StepSize) {
        Insect.Step(StepSize);
        //cout << Insect.Leg.JointX << " " << Insect.Leg.JointY << " ";
        //cout << Insect.Leg.FootX << " " << Insect.Leg.FootY << " ";
        //cout << Insect.Leg.FootState << endl;
    }

    // Display the fitness
    //cout << "Average velocity = " << Insect.cx/RunDuration << endl;





//	double p1 = MapSearchParameter(v[1],-10,10), 
//           p2 = MapSearchParameter(v[2],-10,10);

	return Insect.cx/RunDuration;
}


// The main program

int main (int argc, const char* argv[]) {
  TSearch s(2);
    
  // Configure the search
  s.SetRandomSeed(87632455);
  s.SetEvaluationFunction(Evaluate);
  s.SetSelectionMode(RANK_BASED);
  s.SetReproductionMode(HILL_CLIMBING);
  s.SetPopulationSize(1000);
  s.SetMaxGenerations(250);
  s.SetMutationVariance(0.1);
  s.SetCrossoverProbability(0.5);
  s.SetCrossoverMode(TWO_POINT);
  s.SetMaxExpectedOffspring(1.1);
  s.SetElitistFraction(0.1);
  s.SetSearchConstraint(1);
  s.SetCheckpointInterval(5);
    
  // Run the search
  s.ExecuteSearch();
  
  // Display the best individual found
  cout << s.BestIndividual() << endl;

  return 0;
}
