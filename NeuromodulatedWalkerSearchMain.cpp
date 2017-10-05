// ***************************************************
// An example of Evolving CTRNN controllers for Walkers
// ***************************************************
#include "TSearch.h"
#include "random.h"
#include "CTRNN.h"
#include "LeggedAgent.h"
#include "assert.h"

#define PI 3.141592653589793238

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
const int minReceptor = -1;

//Modulation signal oscillates between these two bounds
//The boundaries of the modulation signal; 0.5 increases by 50%, i.e.  1.5 multiplier
const double maxModulation = 0.5;
const double minModulation = -0.5;


//When turned off, disables modulation and calls normal Step function
const bool modulationEnabled = true;
//Linear oscillation
//Number of oscillations of modulating signal to send
//Assuming 8 maximum steps, to coincide with steps, should be approximately factors of 8
//uses sin function instead of linear increment when true
const bool sinusoidalOscillation = true;
const int externalModulationPeriods = 8;

//calculated based on other constants
const double modulationStepSize =  2 * (maxModulation - minModulation ) *  ( externalModulationPeriods / (RunDuration / StepSize) )  ;
//if set to -1 then use continuous values
const int discreteLevelsOfModulation = 3;



//translate value to discrete set of values
//    level -1 = return continuous value
//    levels 2  =  {min, max}
//    levels 3 =  {min, (max+min)/2, max}
//
double TranslateDoubleToDiscreteValues( double d, int levels ) {
    //-1 means use continuous values)
    if (levels == -1 ) {
        return d;
    }

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


void runTests(bool showTests) {
    
    //for linear increment oscillation
    double modVel= modulationStepSize;
    //for instantenous modulation level
    double modulationLevel = 0;
    //how often to show the current modulation level
    int displayFreq = 100;
    int count=0;
    int hitTopCount=0;
    int hitBotCount=0;
    
    for (double time = 0; time < RunDuration; time += StepSize) {
        //use global modulation enabled to determine step to update    
        //oscillate back and forth between bounds
        if (modulationLevel >= maxModulation ) {
            if ( showTests ) {
                cout << "Hit max going DOWN! @" << time << endl;
            }
            modVel = -modulationStepSize;
            hitTopCount++;
        } else if ( modulationLevel < minModulation ) {
            modVel = modulationStepSize;
            if ( showTests ) {
                cout << "Hit min going UP! @" << time << endl;
            }
            hitBotCount++;
        } 
        modulationLevel += modVel;
        count++;
        if (showTests &&  count % displayFreq == 1) {
            cout << "time: " << time << "  modulation: " << modulationLevel;
            //calculate sin and then scale to modulation bounds
            //used this to debug a silly bug I kept getting
            //double sinCalc = sin(  time / (RunDuration / externalModulationPeriods) * 2 * PI );
            //double center = (maxModulation+minModulation) / 2 ;
            //cout << "center: " << center << endl;
            //double scale = (maxModulation-minModulation )/2;
            //cout << "scale: " << scale << endl;
            //sinCalc =     center + scale  * sinCalc ;
            
            double sinCalc = (maxModulation+minModulation) / 2 + (maxModulation-minModulation )/2 * sin(  time / (RunDuration / externalModulationPeriods) * 2 * PI );
            
            cout << "  vs. sin calculated2: " << sinCalc << endl;
            cout << "    " << ( modulationLevel - sinCalc ) << endl;
            assert(  modulationLevel - sinCalc  < 0.25 );
        }
            
    } 
    
    //verify that the correct number of oscillations occurs when
    assert( hitTopCount == externalModulationPeriods && externalModulationPeriods == hitBotCount );
    cout << "externalModulationPeriods is working properly" << endl;
    
    if ( showTests ) {
        cout << "hitTopCount: "<< hitTopCount << " ==  " << externalModulationPeriods << endl;
    }
    
    double a = MapSearchParameter( -0.9, minReceptor, maxReceptor);
    double b = MapSearchParameter( -0.1, minReceptor, maxReceptor);
    double c = MapSearchParameter( 0.1 , minReceptor, maxReceptor);
    double d = MapSearchParameter( 0.9 , minReceptor, maxReceptor);
    
    int levels=2;
    
    assert( TranslateDoubleToDiscreteValues(a, levels) == minReceptor );
    assert( TranslateDoubleToDiscreteValues(b, levels) == minReceptor );
    assert( TranslateDoubleToDiscreteValues(c, levels) == maxReceptor );
    assert( TranslateDoubleToDiscreteValues(d, levels) == maxReceptor );
    
    cout << "TranslateDoubleToDiscreteValues with 2 values working" << endl;
    
    
    if ( showTests ) {
        levels=2;
        cout << "---------------------------------------------" <<endl;
        cout << "translate -0.9 with 2 levels: " << TranslateDoubleToDiscreteValues(a, levels) << endl;
        cout << "translate -0.1 with 2 levels: " << TranslateDoubleToDiscreteValues(b, levels) << endl;
        cout << "translate 0.1 with 2 levels: " << TranslateDoubleToDiscreteValues(c, levels) << endl;
        cout << "translate 0.9 with 2 levels: " << TranslateDoubleToDiscreteValues(d, levels) << endl;
        
        levels=3;
        cout << "---------------------------------------------" <<endl;
        cout << "translate -0.9 with 3 levels: " << TranslateDoubleToDiscreteValues(a, levels) << endl;
        cout << "translate -0.1 with 3 levels: " << TranslateDoubleToDiscreteValues(b, levels) << endl;
        cout << "translate 0.1 with 3 levels: " << TranslateDoubleToDiscreteValues(c, levels) << endl;
        cout << "translate 0.9 with 3 levels: " << TranslateDoubleToDiscreteValues(d, levels) << endl;
        
        levels=4;
        cout << "---------------------------------------------" <<endl;
        cout << "translate -0.9 with 4 levels: " << TranslateDoubleToDiscreteValues(a, levels) << endl;
        cout << "translate -0.1 with 4 levels: " << TranslateDoubleToDiscreteValues(b, levels) << endl;
        cout << "translate 0.1 with 4 levels: " << TranslateDoubleToDiscreteValues(c, levels) << endl;
        cout << "translate 0.9 with 4 levels: " << TranslateDoubleToDiscreteValues(d, levels) << endl;
    }
    return;
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
       
       double receptorStrength = TranslateDoubleToDiscreteValues(   MapSearchParameter(v[paramCount], minReceptor, maxReceptor), discreteLevelsOfModulation );
       c.SetNeuronReceptor(i, receptorStrength ) ;
       
       //continuous - original
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
          
          if ( sinusoidalOscillation ) {
              //calculate sin and then scale to modulation bounds
              modulationLevel = (maxModulation+minModulation) / 2 + (maxModulation-minModulation )/2 * sin(  time / (RunDuration / externalModulationPeriods) * 2 * PI );
              
              
          } else {
              //oscillate modulationLevel back and forth between bounds
              if (modulationLevel >= maxModulation ) {
                  modVel = -modulationStepSize;
              } else if ( modulationLevel < minModulation ) {
                  modVel = modulationStepSize;
              } 
              modulationLevel += modVel;        
          }

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

  //verify settings are reasonable - true shows info
  cout << "Running tests..." << endl;
  runTests( false );
  //only run tests
  //return -1;
  
  

  TSearch s(  networkSize*neuronParameterCount + networkSize*networkSize   );
    
  // Configure the search
  s.SetRandomSeed( 11235813 );

  s.SetEvaluationFunction(Evaluate);
  s.SetSelectionMode(RANK_BASED);
  s.SetReproductionMode(HILL_CLIMBING);
  s.SetPopulationSize(1000);
  s.SetMaxGenerations(2500);
  
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
  
  cout << "------------------------------------------------------------------" << endl;
  cout << "Best performing agent has the following neuron receptor strengths:" << endl;
  
  int startingReceptor = 2 * networkSize;
  for (int i=1; i <= networkSize; i++ ) {
      double val = TranslateDoubleToDiscreteValues(   MapSearchParameter(s.BestIndividual()[startingReceptor+i], minReceptor, maxReceptor), discreteLevelsOfModulation );
      cout << "Neuron " << i << " has receptor strength: " << val << endl;
  }
  return 0;
}

