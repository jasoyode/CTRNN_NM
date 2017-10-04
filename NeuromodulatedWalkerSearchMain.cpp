// ***************************************************
// An example of Evolving CTRNN controllers for Walkers
// ***************************************************
#include "TSearch.h"
#include "random.h"
#include "CTRNN.h"
#include "LeggedAgent.h"

// Following example in text
// Evolving walking: The anatomy of an evolutionary search (2004)
// by Chad W. Seys , Randall D. Beer
// http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.62.1649&rep=rep1&type=pdf

const double RunDuration = 220;
const double StepSize = 0.1;

//CTRNN constraints
const double minNeuronBiasAndWeights=-16;
const double maxNeuronBiasAndWeights=16;
const double minTimingConstant = 0.5;
const double maxTimingConstant = 10.0;
//Neurons of neurons
const int networkSize = 3;


// ****************************************************
// Added parameters for extrinsic neuromodulation
// ****************************************************

//Number of parameters per neuron ( bias, timingConstant, receptorStrength)
const int neuronParameterCount = 3;

// signal *  (   (1 + mod) * receptor   )  determines multiplicative effect 
//receptor = 0 means no modulation happens (if min=max=0 then no modulation)
//receptor = 1 means full effect
const int maxReceptor = 1;
const int minReceptor = 0;


//Modulation signal oscillates between these two bounds
//The boundaries of the modulation signal 0.5 increases by 50%, i.e.  1.5 multiplier
const double maxModulation = 0.5;
const double minModulation = -0.5;

//Number of oscillations of modulating signal to send
//Assuming 8 maximum steps, to coincide with steps, should be approximately factors of 8
const int externalModulationPeriods = 2;
const double modulationStepSize =  (maxModulation - minModulation ) *  ( externalModulationPeriods / (RunDuration / StepSize) )  ;


//When turned off, disables modulation and calls normal Step function
const bool modulationEnabled = true;


//translate value to discrete set of values
//    levels 2  =  {min, max}
//    levels 3 =  {min, (max+min)/2, max}
//
double TranslateDoubleToDiscreteValues( double d, int levels ) {

    //cout << "d:" << d << " mapped to ";
    double range = maxReceptor - minReceptor;
    double discreteIncrement = range / ( levels -1 );
    double increment = range / levels;

    for (int i=1; i< levels; i++ ) {
    
        if ( d <   (minReceptor + i*increment )   ) {
            //cout <<  (minReceptor +  discreteIncrement*(i-1) )  << endl;
            return minReceptor + discreteIncrement*(i-1);
        }    
    }
    //cout <<  maxReceptor << endl;
    return maxReceptor;
    
       
}



//Evaluate the performance of externally modulated CTRNN controllers with walking task
double Evaluate(TVector<double> &v, RandomState &rs)
{

	// Create a CTRNN 
	// then set values based upon the vector passed in
	CTRNN c( networkSize );
    int paramCount=0;
    
    //first N search parameters are biases
    for (int i=1; i<= networkSize; i++) {
       //setup individual neuron settings, incrementing the vector index as we go
       paramCount++;
       c.SetNeuronBias(i, MapSearchParameter(v[paramCount],minNeuronBiasAndWeights,maxNeuronBiasAndWeights) );
    }
    
    //second N search parameters are timing constants
    for (int i=1; i<= networkSize; i++) {       
       paramCount++;
       c.SetNeuronTimeConstant(i, MapSearchParameter(v[paramCount], minTimingConstant, maxTimingConstant) ) ;

    }
    
    //third N search parameters are receptor strengths
    for (int i=1; i<= networkSize; i++) {
       //this is the double value that regulates how much neurons are impacted by the modulation signal
       paramCount++;
       
       
       //double receptorStrength = discretizeReceptor(   MapSearchParameter(v[paramCount], minReceptor, maxReceptor)       );
       
       double receptorStrength = TranslateDoubleToDiscreteValues(   MapSearchParameter(v[paramCount], minReceptor, maxReceptor), 2 );
       c.SetNeuronReceptor(i, receptorStrength ) ;
       
       //continuous
       //c.SetNeuronReceptor(i, MapSearchParameter(v[paramCount], minReceptor, maxReceptor) ) ;
    }

    //remaining search parameters are synaptic weights
    for (int i=1; i<= networkSize; i++) {
       for (int j=1; j<= networkSize; j++) {
         paramCount++;
         c.SetConnectionWeight(i, j, MapSearchParameter(v[ paramCount  ], minNeuronBiasAndWeights,maxNeuronBiasAndWeights) );
       }
    }
    
    // Randomize the circuit - causes segfault if you don't pass rs
    c.RandomizeCircuitState(-0.5,0.5, rs);


	//Create a One Legged Walker and load the CTRNN
	LeggedAgent Insect;
	Insect.NervousSystem = c;

    // Run the agent must pass rs and use rs or segfault
    SetRandomSeed( rs.GetRandomSeed() );
    Insect.Reset(0, 0, 0, rs);
    
    //instantaneous modulation signal
    double modulationLevel = 0;
    
    //modulation rate of change (modulation velocity)
    //swtiches from positive to negative and vice versa
    double modVel = modulationStepSize;


    for (double time = 0; time < RunDuration; time += StepSize) {
    
      //use global modulatioEnabled to determine whether to use modulation step or not
      if (modulationEnabled) {
          //oscillate modulationLevel back and forth between bounds
          if (modulationLevel >= maxModulation ) {
              modVel = -modulationStepSize;
          } else if ( modulationLevel < minModulation ) {
              modVel = modulationStepSize;
          } 
          modulationLevel += modVel;        
          //I use method chaining to pass this all the way down to the CTRNN where I define a special ModulatedStep function
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
  s.SetRandomSeed( 11235813 );

  s.SetEvaluationFunction(Evaluate);
  s.SetSelectionMode(RANK_BASED);
  s.SetReproductionMode(HILL_CLIMBING);
  s.SetPopulationSize(1000);
  s.SetMaxGenerations(500);
  
  //start with 0.5 (per paper results)
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
  
  //set mutaton variance to 0.05per paper results
  s.SetMutationVariance(0.05);
  s.SetSearchTerminationFunction(NULL);
  s.ExecuteSearch();
    
  // Display the best individual found
  cout << s.BestIndividual() << endl;

  return 0;
}


// The second main program to test impact of modulation on performance of Walker from file
// May be broken as the cpg.ns will not include receptors, so cannot use receptors
int alternate_test_main(int argc, char* argv[])
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

