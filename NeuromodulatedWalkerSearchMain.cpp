// ***************************************************
// An example of Evolving CTRNN controllers for Walkers
// ***************************************************

#include "TSearch.h"
#include "random.h"
#include "CTRNN.h"
#include "LeggedAgent.h"


const double RunDuration = 220;
const double StepSize = 0.1;
const double minVal=-16;
const double maxVal=16;
const double minTiming = 0.5;
const double maxTiming = 10.0;

const int networkSize = 3;
const int neuronParameterCount = 3;

const int maxReceptor = 1;
const int minReceptor = -1;

//increase by 50%
const double maxModulation = 0.5;
const double minModulation = -0.5;

const int externalModulationPeriods = 10;
const double modulationStepSize =  externalModulationPeriods / (RunDuration / StepSize)  ;
const bool modulationEnabled = true;


//Evaluate the performance of CTRNN controllers with walkers
double Evaluate(TVector<double> &v, RandomState &rs)
{

    //debug to verify reasonable values for genome
    //cout << v[1] << "->v1  "  <<  v[2] << "->v2 "  <<v[3] << "->v3 "  <<v[4] << "->v4 "  <<v[5] << "->v5 "  << v[6] << "->v6 "  << endl; 

	//Create a CTRNN from the vector passed in
	CTRNN c( networkSize );

//*    
    int paramCount=0;
    
    for (int i=1; i<= networkSize; i++) {
       //setup individual neuron settings
       paramCount++;
       c.SetNeuronBias(i, MapSearchParameter(v[paramCount],minVal,maxVal) );
       paramCount++;
       c.SetNeuronTimeConstant(i, MapSearchParameter(v[paramCount], minTiming, maxTiming) ) ;
       paramCount++;
       c.SetNeuronReceptor(i, MapSearchParameter(v[paramCount], minReceptor, maxReceptor) ) ;
       for (int j=1; j<= networkSize; j++) {
         paramCount++;
         c.SetConnectionWeight(i, j, MapSearchParameter(v[ paramCount  ],minVal,maxVal) );
       }
    }
    
    // Randomize the circuit - causes segfault when running multitrheaded
    c.RandomizeCircuitState(-0.5,0.5, rs);


	//Create a One Legged Walker from the CTRNN
	LeggedAgent Insect;
	Insect.NervousSystem = c;

    // Run the agent
    SetRandomSeed( rs.GetRandomSeed() );
    Insect.Reset(0, 0, 0, rs);
    
    double modulationLevel = 0;
    double modVel = modulationStepSize;

    for (double time = 0; time < RunDuration; time += StepSize) {
    
      //use global modulation enabled to determine step to update    
      if (modulationEnabled) {
          //oscillate back and forth between bounds
          if (modulationLevel >= maxModulation ) {
              modVel = -modulationStepSize;
          } else if ( modulationLevel < minModulation ) {
              modVel = modulationStepSize;
          } 
          modulationLevel += modVel;        
          Insect.ModulatedStep(StepSize, modulationLevel);
        
        } else {
          //regular step
          Insect.Step(StepSize);
        
        }
    }
	return Insect.cx/RunDuration;
}


//two stage evolution, switching the mutation variance after 0.126 fitness is achieved
int MyTerminationFunction(int Generation,  double BestPerf,  double AvgPerf,  double PerfVar)  {
  if (BestPerf > 0.126) 
      return 1;
  else 
      return 0;
}



// The main program
int main (int argc, const char* argv[]) {
  TSearch s(  networkSize*neuronParameterCount + networkSize*networkSize   );
    
  // Configure the search
//  s.SetRandomSeed(87632455);
  s.SetRandomSeed( 42 );

  s.SetEvaluationFunction(Evaluate);
  s.SetSelectionMode(RANK_BASED);
  s.SetReproductionMode(HILL_CLIMBING);
  s.SetPopulationSize(1000);
  s.SetMaxGenerations(2500);
  
  //start with 0.5
  s.SetMutationVariance(0.5);
  
  s.SetCrossoverProbability(0.5);
  s.SetCrossoverMode(TWO_POINT);
  s.SetMaxExpectedOffspring(1.1);
  s.SetElitistFraction(0.1);
  s.SetSearchConstraint(1);
  s.SetCheckpointInterval(5);
    
  /* Stage 1 */
  s.SetSearchTerminationFunction(MyTerminationFunction);
  s.ExecuteSearch();
  
  
  /* STAGE 2 */
  cout << "Stage 2 Begins!" <<endl;
  
  //set mutaton variance to 0.05
  s.SetMutationVariance(0.05);
  s.SetSearchTerminationFunction(NULL);
  s.ExecuteSearch();
    
    
  
  // Display the best individual found
  cout << s.BestIndividual() << endl;

  return 0;
}


// The second main program to test impact of modulation on performance of Walker from file
int main2(int argc, char* argv[])
{
    LeggedAgent Insect;

    // Load the CTRNN into the agent
    char fname[] = "cpg.ns";
    ifstream ifs;
    ifs.open(fname);
    if (!ifs) {
        cerr << "File not found: " << fname << endl;
        exit(EXIT_FAILURE);
    }
    ifs >> Insect.NervousSystem;

    // Run the agent
    SetRandomSeed( 1 ); //RandomSeed);
    Insect.Reset(0, 0, 0);
    
    double modVel=0;
    double modulationLevel=0;

    for (double time = 0; time < RunDuration; time += StepSize) {
            
        //use global modulation enabled to determine step to update    
        if (modulationEnabled) {
            //oscillate back and forth between bounds
            if (modulationLevel >= maxModulation ) {
                modVel = -modulationStepSize;
            } else if ( modulationLevel < minModulation ) {
                modVel = modulationStepSize;
            } 
            modulationLevel += modVel;        
            Insect.ModulatedStep(StepSize, modulationLevel);
        
        } else {
            //regular step
            Insect.Step(StepSize);
        
        }
        //cout << Insect.Leg.JointX << " " << Insect.Leg.JointY << " ";
        //cout << Insect.Leg.FootX << " " << Insect.Leg.FootY << " ";
        //cout << Insect.Leg.FootState << endl;
    }

    // Display the fitness
    cout << "Average velocity = " << Insect.cx/RunDuration << endl;

    // Finished
    return 0;
}

