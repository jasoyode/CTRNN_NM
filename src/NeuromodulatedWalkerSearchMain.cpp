// ***************************************************
// An example of Evolving CTRNN controllers for Walkers
// ***************************************************
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <array>
#include <algorithm>
#include <sys/stat.h>
#include <cstring>
#include <cstdlib>
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include <iterator>
#include "TSearch.h"
#include "random.h"
#include "CTRNN.h"
#include "LeggedAgent.h"
#include "assert.h"
#include "ini.h"
#include "INIReader.h"

#define PI 3.141592653589793238

// Following example in text
// Evolving walking: The anatomy of an evolutionary search (2004)
// by Chad W. Seys , Randall D. Beer
// http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.62.1649&rep=rep1&type=pdf

//NOT CONST so that they can be set from config file
double RunDuration;
double StepSize;

double Stage1Threshold;

//whether or not to show the test debugging text
const bool diplayTestText = false;

//settings loaded from config file
int NeuromodulationType;
double minNeuronBiasAndWeights;
double maxNeuronBiasAndWeights;
double minTimingConstant;
double maxTimingConstant;
double minSensorWeights;
double maxSensorWeights;
bool mixedPatternGen;
bool mixedPatternGenSingleRun;

bool recordAllActivity;


int networkSize;
int neuronParameterCount;
int maxReceptor;
int minReceptor;
double maxModulation;
double minModulation;
bool sinusoidalOscillation;
double externalModulationPeriods;
double modulationStepSize;
int discreteLevelsOfModulation;

//experiment settings
int popSize;
int generations;
int runs;
int startingSeed;


//file handle to write result to file
ofstream expLogFile;
ofstream bestAgentGenomeLogFile;
ofstream bestAgentPhenotypeLogFile;

ofstream bestAgentFitnessAndReceptorLogFile;
ofstream recordLog;

//name of experiment as passed in through command argument
char* expName;


// https://stackoverflow.com/questions/18100097/portable-way-to-check-if-directory-exists-windows-linux-c
int dirExists(const char *pathname)
{
    struct stat info;
	if( stat( pathname, &info ) != 0 ) {
	    printf( "cannot access %s\n parent folder might not exist yet\n", pathname );
		return -1;
	}
	else if( info.st_mode & S_IFDIR ) {  // S_ISDIR() doesn't exist on my windows 
    	printf( "%s is a directory\n", pathname );
		return 1;
	} else {
	    printf( "%s is no directory\n", pathname );
		return 0;
	}
	return -1;
}


// https://stackoverflow.com/questions/478898/how-to-execute-a-command-and-get-output-of-command-within-c-using-posix
// Using this function to get output from command
//
std::string exec(const char* cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::shared_ptr<FILE> pipe(popen(cmd, "r"), pclose);
    if (!pipe) throw std::runtime_error("popen() failed!");
    while (!feof(pipe.get())) {
        if (fgets(buffer.data(), 128, pipe.get()) != nullptr)
            result += buffer.data();
    }
    return result;
}

//translate value to discrete set of values
//    level -1 = return continuous value
//    levels 2  =  {min, max}
//    levels 3 =  {min, (max+min)/2, max}
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


//*****************************************
//
//*****************************************
// Translate the second vector to be the phenotype of the genotype v
void translate_to_phenotype(TVector<double> &v, TVector<double> &pheno)
{
    int paramCount=0;
    //first N search parameters are biases
    for (int i=1; i<= networkSize; i++) {
       //setup individual neuron settings, incrementing the vector index as we go
       paramCount++;
       pheno(paramCount) = MapSearchParameter(v[paramCount], minNeuronBiasAndWeights,maxNeuronBiasAndWeights) ;
    }
    //second N search parameters are timing constants
    for (int i=1; i<= networkSize; i++) {       
       paramCount++;
       pheno(paramCount) =  MapSearchParameter(v[paramCount], minTimingConstant, maxTimingConstant)  ;
    }
    //third N search parameters are receptor strengths
    for (int i=1; i<= networkSize; i++) {
       //this is the double value that regulates how much neurons are impacted by the modulation signal
       paramCount++;
       double receptorStrength = TranslateDoubleToDiscreteValues(   MapSearchParameter(v[paramCount], minReceptor, maxReceptor), discreteLevelsOfModulation );
       pheno(paramCount) = receptorStrength  ;
    }
    
    //remaining search parameters are synaptic weights
    for (int i=1; i<= networkSize; i++) {
       for (int j=1; j<= networkSize; j++) {
         paramCount++;
         pheno(paramCount) = MapSearchParameter(v[ paramCount  ], minNeuronBiasAndWeights,maxNeuronBiasAndWeights) ;
       }
    }
    
    //remaining search parameters are sensor synaptic weights
    for (int i=1; i<= networkSize; i++) {
       paramCount++;
       pheno(paramCount) = MapSearchParameter(v[ paramCount  ], minSensorWeights, maxSensorWeights ) ;
    }
    
    return;
}




//*****************************************************
// this version does not log to file
//*****************************************************

//Evaluate the performance of externally modulated CTRNN controllers with walking task
double Evaluate(TVector<double> &v, RandomState &rs)
{
    
    int runsToDo = 1;
    int totalRuns = 1;
    float fitness = 0;
    
    if ( mixedPatternGen && !mixedPatternGen ) {
      runsToDo++ ;  
      totalRuns++;
    }

    while (runsToDo > 0) {
      runsToDo--;


      // Create a CTRNN 
      // then set values based upon the vector passed in
      CTRNN c( networkSize );
      int paramCount=0;
      
      //first N search parameters are biases
      for (int i=1; i<= networkSize; i++) {
         //setup individual neuron settings, incrementing the vector index as we go
         paramCount++;
         c.SetNeuronBias(i, MapSearchParameter(v[paramCount], minNeuronBiasAndWeights,maxNeuronBiasAndWeights) );
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
      
      
      //map to track the weights of the sensors
      //std::map <int, double> sensorWeights;
      TVector<double> sensorWeights(1, networkSize);
      
      //remaining search parameters are sensor synaptic weights
      for (int i=1; i<= networkSize; i++) {
        paramCount++;
        sensorWeights(i)= MapSearchParameter(v[ paramCount  ], minSensorWeights, maxSensorWeights ) ;
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
        // void SetNeuronExternalInput(int i, double value) {externalinputs[i] = value;};
        // for 1 to n ...   c.SetNeuronExternalInput( i,   weight_i* Insect.Leg.Angle );
        // external input modulated by default
        //Provide input from sensors regardless of modulation
        for (int i=1; i<= networkSize; i++) {
          
          //if not single run mode, then run two full evaluations
          if (!mixedPatternGenSingleRun ) {
            //if mixedPatternGen and first test turn off, otherwise send sensor angle data
            if ( mixedPatternGen && runsToDo == 1 ) {
              Insect.NervousSystem.SetNeuronExternalInput( i, 0 );
            } else {
              Insect.NervousSystem.SetNeuronExternalInput( i, sensorWeights(i) * Insect.Leg.Angle );
            }
          } else {
            //if single run mode, then half way through change
            if ( mixedPatternGen && time < RunDuration/2 ) {
              Insect.NervousSystem.SetNeuronExternalInput( i, 0 );
            } else {
              Insect.NervousSystem.SetNeuronExternalInput( i, sensorWeights(i) * Insect.Leg.Angle );
            }
          }
          
        }
      
        //use global modulatioEnabled to determine whether to use modulation step or not
        if (  NeuromodulationType != 0 ) {
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
            Insect.ModulatedStep(StepSize, modulationLevel, NeuromodulationType);
          } else {
            //regular step
            Insect.Step(StepSize);
          }
          
      }
      fitness += Insect.cx/RunDuration;
    }      
    
	return fitness/totalRuns ;
}


// TODO: add method that takes a CTRNN and vector and loads it


///**************************************************
// This is the version that records to a log file
//***************************************************
//Evaluate the performance of externally modulated CTRNN controllers with walking task
double Evaluate(TVector<double> &v, ostream &recordLog = std::cout)
{

    int runsToDo = 1;
    int totalRuns = 1;
    float fitness = 0;
    
    if ( mixedPatternGen && !mixedPatternGenSingleRun ) {
      runsToDo++;  
      totalRuns++;
    }

    while (runsToDo > 0) {
      runsToDo--;

	  //////////////////////

      bool fileOut = true;
      if (&recordLog == &std::cout) {
        fileOut = false;
      }
      // Create a CTRNN 
      // then set values based upon the vector passed in
      CTRNN c( networkSize );
      int paramCount=0;
      
      //first N search parameters are biases
      for (int i=1; i<= networkSize; i++) {
         //setup individual neuron settings, incrementing the vector index as we go
         paramCount++;
         c.SetNeuronBias(i, MapSearchParameter(v[paramCount], minNeuronBiasAndWeights,maxNeuronBiasAndWeights) );
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
      
      //map to track the weights of the sensors
      //std::map <int, double> sensorWeights;
      TVector<double> sensorWeights(1, networkSize);
      
      //remaining search parameters are sensor synaptic weights
      for (int i=1; i<= networkSize; i++) {
        paramCount++;
        sensorWeights(i)= MapSearchParameter(v[ paramCount  ], minSensorWeights, maxSensorWeights ) ;
      }
      
     
      // Randomize the circuit - 
      c.RandomizeCircuitState(-0.5,0.5);

      //Create a One Legged Walker and load the CTRNN
      LeggedAgent Insect;
      Insect.NervousSystem = c;

      //TODO is this ok?
      SetRandomSeed( 0 );
      Insect.Reset(0, 0, 0);
      
      //instantaneous modulation signal
      double modulationLevel = 0;
      
      //modulation rate of change (modulation velocity)
      //swtiches from positive to negative and vice versa
      double modVel = modulationStepSize;

      
      //RECORDING BEST PERF
      //setup header for logfile when passed
      //do not even write this unless recordAllActivity is true!
      if ( fileOut && (runsToDo == totalRuns-1)  && recordAllActivity ) { // recordLog ) {
        
        recordLog << "time,modulation,jointX,jointY,footX,footY,FootState,cx,angle,omega,run";
        for (int i=1; i <= networkSize; i++) {
          recordLog << ",n" << i << "_out";
        }
        recordLog << endl;
        
      }

      for (double time = 0; time < RunDuration; time += StepSize) {
        // void SetNeuronExternalInput(int i, double value) {externalinputs[i] = value;};
        // for 1 to n ...   c.SetNeuronExternalInput( i,   weight_i* Insect.Leg.Angle );
        // external input modulated by default
        
        
        if ( !mixedPatternGenSingleRun) {
          //Provide input from sensors regardless of modulation
          for (int i=1; i<= networkSize; i++) {
            //if mixedPatternGen and first test turn off, otherwise send sensor angle data
              if ( mixedPatternGen && runsToDo == 1 ) {
                Insect.NervousSystem.SetNeuronExternalInput( i, 0 );
              } else {
                Insect.NervousSystem.SetNeuronExternalInput( i, sensorWeights(i) * Insect.Leg.Angle );
              }
          }
        } else {
        
          //Provide input from sensors regardless of modulation
          for (int i=1; i<= networkSize; i++) {
            //if mixedPatternGenSingleRun and first half of time, otherwise send sensor angle data
              if ( mixedPatternGen && time >= RunDuration/2 ) {
                Insect.NervousSystem.SetNeuronExternalInput( i, 0 );
              } else {
                Insect.NervousSystem.SetNeuronExternalInput( i, sensorWeights(i) * Insect.Leg.Angle );
              }
          }
        
        }
        
        //use global modulatioEnabled to determine whether to use modulation step or not
        if (  NeuromodulationType != 0 ) {
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
            Insect.ModulatedStep(StepSize, modulationLevel, NeuromodulationType);
          } else {
            //regular step
            Insect.Step(StepSize);
          }
          
          //RECORDING BEST PERF
          if ( fileOut &&  recordAllActivity ) { // || ( time + StepSize >= RunDuration  )  ) ) { // recordLog ) {
            recordLog << time << "," << modulationLevel << ",";
            recordLog << Insect.Leg.JointX << "," << Insect.Leg.JointY << ",";
            recordLog << Insect.Leg.FootX << "," << Insect.Leg.FootY << ",";
            recordLog << Insect.Leg.FootState << "," << Insect.cx << "," << Insect.Leg.Angle << "," << Insect.Leg.Omega << "," << runsToDo ;
            //write outputs of neurons
            for (int i=1; i <= networkSize; i++) {
              recordLog << "," <<   Insect.NervousSystem.outputs[i] ;
            }
            recordLog << endl;
          }
      }
      fitness += Insect.cx/RunDuration;

	}
	return fitness/totalRuns;

}


//two stage evolution, switching the mutation variance after 0.126 from paper fitness is achieved
int MyTerminationFunction(int Generation,  double BestPerf,  double AvgPerf,  double PerfVar)  {
  if (BestPerf >  Stage1Threshold ) 
      return 1;
  else 
      return 0;
}




//Evaluate a mutation, by specifying a particular position mutate and by a certain amount
double EvaluateMutants2(TVector<double> &v, int parameterNum, double mutation ) {
    TVector<double> mutatedVector( v );
    mutatedVector(parameterNum) =  mutation;
    return Evaluate(mutatedVector);
}

string EvaluateMutants(TVector<double> &v, int parameterNum1, double mutation1, int parameterNum2, double mutation2 ) {
    TVector<double> mutatedVector( v );
    
    
    /*
    param_map[19] = "wALL";
    param_map[20] = "w*-to-1";
    param_map[21] = "w*-to-2";
    param_map[22] = "w*-to-3";
    param_map[23] = "w*-to-1or2";
    param_map[24] = "w*-to-1or3";
    param_map[25] = "w*-to-2or3";
    */
    
    //sets upper and lower percentage modifier
    double MAX = 0.5;
    
    
    //cout << "parameterNum1" <<parameterNum1 << endl;
    //exit(-1);
    
    if (parameterNum1 == 22 ) {
      //cout << "ADJUST ALL WEIGHTS IN NETWORK BY %" <<endl;
      for (int i=10; i<22; i++) {
        mutatedVector(i) = mutatedVector(i) * (1 + mutation1*MAX );
      }
      
    } else {
      mutatedVector(parameterNum1) = mutation1;
    }
    
    if (parameterNum2 == 22 ) {
      //cout << "ADJUST ALL WEIGHTS IN NETWORK BY %" <<endl;
      for (int i=10; i<22; i++) {
        mutatedVector(i) = mutatedVector(i) * (1 + mutation2*MAX );
      }
      
    } else {
      mutatedVector(parameterNum2) = mutation2;
    }
    
    double fitness = Evaluate(mutatedVector);
    int genomeSize = v.Size();
    
    //translate resultant network into phenotype
    TVector<double> phenotype(1, genomeSize);
    translate_to_phenotype( mutatedVector, phenotype );
    
    //STARTHERE NEED TO FIX OUT OF BOUNDS
    
    double paramVal1=-1;
    double paramVal2=-1;
    
    if (parameterNum1 == 22 ) {
      paramVal1 = 1 + mutation1*MAX;
    } else {
      paramVal1 = phenotype(parameterNum1);
    }
    
    if (parameterNum2 == 22 ) {
      paramVal2 = 1 + mutation2*MAX;
    } else {
      paramVal2 = phenotype(parameterNum2);
    }
    
    
    //DEBUGGING
    TVector<double> phenotype_orig(1, genomeSize);
    translate_to_phenotype( v, phenotype_orig );
    
    
    ostringstream stream;
    stream << paramVal1 <<  "," << paramVal2 << "," << fitness << ",";
    string s = stream.str();
    
    
    
    /*
    if (minNeuronBiasAndWeights > phenotype(parameterNum1) || minNeuronBiasAndWeights > phenotype(parameterNum2)  ) {
      cout << "Genome1:  " << v(parameterNum1) << " + " << mutation1 << " = " << mutatedVector(parameterNum1) << endl;
      cout << "Phenome1: " << phenotype_orig(parameterNum1) << " + " << mutation1 << " = " << phenotype(parameterNum1) << endl;
      cout << "Genome2:  " << v(parameterNum2) << " + " << mutation2 << " = " << mutatedVector(parameterNum2) << endl;
      cout << "Phenome2: " << phenotype_orig(parameterNum2) << " + " << mutation2 << " = " << phenotype(parameterNum2) << endl;
      cout << "  Fitness " << fitness << endl;
      cout << "     " << s << endl;
      cout << "minNeuronBiasAndWeights " << minNeuronBiasAndWeights <<endl;
      
      
      cout << "What is happening?" << phenotype(parameterNum1) << "   " << phenotype(parameterNum2)  <<endl;;
      exit(-1);
    }
    */
    
    
    return s;
}



void runTests(bool showTests) {
    
    //for linear increment oscillation
    double modVel= modulationStepSize;
    //for instantaneous modulation level
    double modulationLevel = 0;
    //how often to show the current modulation level
    int displayFreq = 100;
    int count=0;
    int hitTopCount=0;
    int hitBotCount=0;
    
    //cout << "checkpoint1: " << "  modVel: " << modVel << endl;
    
    if ( NeuromodulationType != 0 ) {
      
      for (double time = 0; time < RunDuration; time += StepSize) {
          
          //use global modulation enabled to determine step to update    
          //oscillate back and forth between bounds
          if (modulationLevel >= maxModulation ) {
              if ( showTests ) {
                  cout << "Hit max going DOWN! @" << time << " because " << modulationLevel << " >= " <<  maxModulation << endl;
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
          
          //cout << "checkpoint2: " << "  modulationLevel: " << modulationLevel << endl;
          
          count++;
          if (showTests &&  count % displayFreq == 1) {
              cout << "time: " << time << "  modulationLevel: " << modulationLevel;
              //calculate sin and then scale to modulation bounds
              //used this to debug a silly bug I kept getting
              //double sinCalc = sin(  time / (RunDuration / externalModulationPeriods) * 2 * PI );
              //double center = (maxModulation+minModulation) / 2 ;
              //cout << "center: " << center << endl;
              //double scale = (maxModulation-minModulation )/2;
              //cout << "scale: " << scale << endl;
              //sinCalc =     center + scale  * sinCalc ;
              
              double sinCalc = (maxModulation+minModulation) / 2 + (maxModulation-minModulation )/2 * sin(  time / (RunDuration / externalModulationPeriods) * 2 * PI );
              cout <<  "  vs. sin calculated2: " << sinCalc << endl;
              cout << "    " << ( modulationLevel - sinCalc ) << endl;
              assert(  modulationLevel - sinCalc  < 0.25 );
          }
              
      } 
      
      //verify that the correct number of oscillations occurs when
      cout << "hitTopCount: " << hitTopCount <<  "   externalModulationPeriods: " << externalModulationPeriods << "  hitBotCount: " << hitBotCount << endl;
      
      //assert( hitTopCount == externalModulationPeriods && externalModulationPeriods == hitBotCount );
      cout << "externalModulationPeriods is working properly" << endl;
      
    }      
    
    
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




void myDisplayFn(int Generation,double BestPerf,double AvgPerf,double PerfVar) {
    expLogFile  << Generation << "," << BestPerf<< "," <<  AvgPerf << "," << PerfVar << endl;
}


void loadValuesFromConfig( INIReader &reader) {

    NeuromodulationType     = reader.GetInteger("mod","NeuromodulationType", 0 ); 

    minNeuronBiasAndWeights = reader.GetReal("ctrnn", "minNeuronBiasAndWeights", -16 );
    maxNeuronBiasAndWeights = reader.GetReal("ctrnn", "maxNeuronBiasAndWeights", 16 );
    minTimingConstant       = reader.GetReal("ctrnn", "minTimingConstant", 0.5 );
    maxTimingConstant       = reader.GetReal("ctrnn", "maxTimingConstant", 10 );
    
    
    minSensorWeights = reader.GetReal("ctrnn", "minSensorWeights", 0 );
    maxSensorWeights = reader.GetReal("ctrnn", "maxSensorWeights", 0 );
    mixedPatternGen =  reader.GetBoolean("ctrnn", "mixedPatternGen", false );
    mixedPatternGenSingleRun = reader.GetBoolean("ctrnn", "mixedPatternGenSingleRun", false );
    
    //cout << "minNeuronBiasAndWeights=" << minNeuronBiasAndWeights << endl;
    //cout << "minSensorWeights" <<minSensorWeights << endl;
    //cout << "maxSensorWeights" <<maxSensorWeights << endl;
    //cout << "mixedPatternGen" <<mixedPatternGen << endl;
    //exit(-1);
    
    
    
    networkSize                = reader.GetInteger("network","networkSize", 0);
    neuronParameterCount       = reader.GetInteger("network","neuronParameterCount", 3);

    maxReceptor                = reader.GetReal("receptor", "maxReceptor", 1 ); 
    minReceptor                = reader.GetReal("receptor", "minReceptor", -1 );
    discreteLevelsOfModulation = reader.GetInteger("receptor", "discreteLevelsOfModulation", 3 );

    //CHANGE BELOW TO modsignal
    
    maxModulation              = reader.GetReal("modsignal", "maxModulation", 0.5 );
    minModulation              = reader.GetReal("modsignal", "minModulation", -0.5 );
    
    sinusoidalOscillation      = reader.GetBoolean("modsignal", "sinusoidalOscillation", true );
    externalModulationPeriods  = reader.GetReal("modsignal", "externalModulationPeriods", 1 );
    
    //cout << "maxModulation" << maxModulation << endl;
    //cout << "minModulation" << minModulation << endl;
    //cout << "RunDuration" << RunDuration << endl;
    //cout << "StepSize" << StepSize << endl;
    //cout << "externalModulationPeriods" << externalModulationPeriods << endl;
    
    popSize      = reader.GetInteger("exp", "popSize", 100 );
    generations  = reader.GetInteger("exp", "generations", 10 );
    runs         = reader.GetInteger("exp", "runs", 10 );
    startingSeed = reader.GetInteger("exp", "startingSeed", 42 );
    RunDuration  = reader.GetReal("exp", "RunDuration", 220);
    StepSize     = reader.GetReal("exp", "StepSize", 0.1 );
    Stage1Threshold = reader.GetReal("exp", "Stage1Threshold", 0.126 );
    
    recordAllActivity = reader.GetBoolean("exp", "recordAllActivity", true );
    
    modulationStepSize =  2 * (maxModulation - minModulation ) *  ( externalModulationPeriods / (RunDuration / StepSize) )  ;
//    cout << "modulationStepSize: " << modulationStepSize << endl;


}


void generateActivityLogsFromGenomes(const char* ini, const char* directory, const char* label, int start1=-1, int stop1=-2, int start2=-1, int stop2=-2) {

  cout << "generateActivityLogsFromGenomes " << endl;
  cout << "directory: " <<directory << endl;
  cout << "label: " <<label << endl;
  
  //use array works
  char dirPath[200];
  //strcpy( dirPath, "DATA/");
  //strcat(dirPath, expName );
  strcpy( dirPath, expName);
  strcat(dirPath, "/" );
  strcat(dirPath, label );
  
  
  char mkdir_command[100];
  strcpy( mkdir_command, ("mkdir -p ") );
  strcat( mkdir_command, dirPath );
  const int dir_err = system( mkdir_command );
     	
  if (-1 == dir_err) {
    printf("Error creating directory!n");
    exit(1);
  } 
  
  
  if ( start1 != -1 ) {
    cout << "Parameters: " << start1 << " -> " << stop1 << ", " << start2 << " -> " << stop2 << endl;
  } else {
    cout << "Non-mutation mode running." << endl;
    string bestAgentFitnessAndReceptorLogFilename( dirPath   );
    bestAgentFitnessAndReceptorLogFilename = bestAgentFitnessAndReceptorLogFilename + "/seeds_tested_fitness.csv";
    
    if ( !recordAllActivity ) {
      bestAgentFitnessAndReceptorLogFile.open( bestAgentFitnessAndReceptorLogFilename );
      bestAgentFitnessAndReceptorLogFile << "seed,fitness," << endl;
      bestAgentFitnessAndReceptorLogFile.close();
    }
                            
  }
  
  
  
  //Copy fitness and receptors into the destination folder  
  char cp_fitness_and_receptors_command[200];
  strcpy( cp_fitness_and_receptors_command, ("cp ") );
  //strcat( cp_fitness_and_receptors_command, "DATA/" );
  strcat( cp_fitness_and_receptors_command, expName );
  //strcat( cp_fitness_and_receptors_command, "/fitness_and_receptors.txt DATA/" );
  
  strcat( cp_fitness_and_receptors_command, "/fitness_and_receptors.txt " );
  strcat( cp_fitness_and_receptors_command, expName );
  strcat( cp_fitness_and_receptors_command, "/" );
  strcat( cp_fitness_and_receptors_command, label );
  strcat( cp_fitness_and_receptors_command, "/fitness_and_receptors.txt" );
  
  
  const int cp_err = system( cp_fitness_and_receptors_command );
  if (-1 == cp_err) {
      printf("Error copying files to new directory!n");
      exit(1);
  }
  
  
  //Copy genomes into the destination folder  
  char cp_genomes_command[200];
  strcpy( cp_genomes_command, ("cp ") );
  strcat( cp_genomes_command, expName );
  strcat( cp_genomes_command, "/genomes.txt " );
  strcat( cp_genomes_command, expName );
  strcat( cp_genomes_command, "/" );
  strcat( cp_genomes_command, label );
  strcat( cp_genomes_command, "/genomes.txt" );
  
  
  const int cp_err2 = system( cp_genomes_command );
  if (-1 == cp_err2) {
      printf("Error copying files to new directory!n");
      exit(1);
  }
  
  cout << "Generating Standard and Altered Testing Data from dir: " << directory  << endl; 

  //use argument passed in to load from config file
  INIReader reader( ini   );
  
  cout << "trying reader" << endl;
  if (reader.ParseError() < 0) {
    std::cout << "Can't load '.ini' file!\n";
    return;
  }
  
  //load global variable values from reader
  cout <<"trying to load values from config " << endl;
  loadValuesFromConfig( reader );  
  cout << "values loaded" << endl;
  //cout << StepSize << " ..";
  
  int genomeSize = (networkSize*neuronParameterCount + networkSize*networkSize);
  
  string phenotypeFilename( dirPath  );
  phenotypeFilename += "/phenotypes.txt";
      
  bestAgentPhenotypeLogFile.open( phenotypeFilename, std::fstream::trunc );  

  
  bestAgentPhenotypeLogFile << "seed,";
  cout << "seed," << endl;
  for (int i=1; i <= networkSize; i++ ) 
      bestAgentPhenotypeLogFile << "bias" << i << ",";
  for (int i=1; i <= networkSize; i++ ) 
      bestAgentPhenotypeLogFile << "timConst" << i << ",";
  for (int i=1; i <= networkSize; i++ ) 
      bestAgentPhenotypeLogFile << "recep" << i << ",";
  for (int i=1; i <= networkSize; i++ ) { 
    for (int j=1; j <= networkSize; j++ ) {
      bestAgentPhenotypeLogFile << "w_" << i << "->" << j << ",";   
    } 
  }
  
  cout << "A" << endl;
  
  for (int i=1; i <= networkSize; i++ ) { 
    bestAgentGenomeLogFile << "w_AS->" << i << ",";   
  }
  cout << "B" << endl;
  
  bestAgentPhenotypeLogFile << endl;
  bestAgentPhenotypeLogFile.close();  

  
  //cout << "TVector of size: " << genomeSize << " must be created!" << endl;

  char genomesFile[100];
  strcpy(genomesFile, directory);
  strcat(genomesFile, "genomes.txt" );
  
  std::ifstream infile( genomesFile );
  
  std::string line;
  bool first=true;
  
  cout << "C" << endl;
  
  cout << "inflie:" << genomesFile << endl;
  
  for( std::string line; getline( infile, line ); )  {
  
  
      
      cout << "line: " << line << endl;
      //...for each line in input...
      // each line is a separate genome previously recorded
      //the first line is a header
      if (first) {
        first = false;
        continue;
      }
      //remove commas and replace with white space
      std::replace( line.begin(), line.end(), ',', ' '); // replace all ',' to ' '
      int seed;

      //create space for genome!
      TVector<double> genome(1,1);
      genome.SetSize( genomeSize );
      
      //istringstream iss( genome_string );
      istringstream iss( line );
      
      /////////////////////
      bool first_val = true;
      int i=1;
      
      while (i <=  genomeSize &&  iss) {
        string subs;
        iss >> subs;
        if ( first_val) {
          first_val = false;
          seed = stoi( subs );
          cout << "Seed set to be: " << seed << endl;
          
          
          
        } else {
          cout << genome.Size() << endl;
          cout << "i:" << i << endl;
          cout << "lower: "<<genome.LowerBound() << endl;
          cout << "upper: "<<genome.UpperBound() << endl;
          
          try {
            genome(i) = stof( subs );
          } catch (const std::invalid_argument& ia) {
              cout << "Invalid argument: " << ia.what() << '\n';
              cout << "Did you select an appropriately sized config file?" << "\n";
              std::exit(-1);
          }
          cout << " genome[" << i << "]:" << genome(i) << endl ;
          i++;
        }
        
      }
      
      //to make this inclusive according to
      if ( seed < startingSeed  || seed >=  (startingSeed + runs) ) {
        continue;
      }
      
      TVector<double> phenotype(1, genomeSize);
      
      translate_to_phenotype( genome, phenotype );
      //cout << "phenotype converted!" << endl;
      
      
      string phenotypeFilename( dirPath  );
      phenotypeFilename += "/phenotypes.txt";
      
      bestAgentPhenotypeLogFile.open( phenotypeFilename, std::fstream::app );  
      bestAgentPhenotypeLogFile << ( seed ) << ",";
      for (int i=1; i <= phenotype.Size(); i++ ) {
        bestAgentPhenotypeLogFile << phenotype[i] << ",";
      }
      bestAgentPhenotypeLogFile <<  endl;
      bestAgentPhenotypeLogFile.close();
      
	  
	  //create from base path each time
      string recordFilename2( dirPath  );
      recordFilename2 += "/seed_" + std::to_string( seed )  + "_recorded_activity.csv";

      //do not even open it unless specified!
      if (recordAllActivity) {
        recordLog.open(  recordFilename2  );
      } 
      
      //store generated data (original or test) for comparison
      double origFit = Evaluate(genome,   recordLog );
      
      cout << "origFit: " << origFit << endl;
      
      if (recordAllActivity) {
        recordLog.close();
      }
      
      
      
      string bestAgentFitnessAndReceptorLogFilename( dirPath   );
      bestAgentFitnessAndReceptorLogFilename = bestAgentFitnessAndReceptorLogFilename + "/seeds_tested_fitness.csv";

      //if we are in recordAllActivity mode, then we don't want to overwrite this!
      if ( !recordAllActivity ) {
        bestAgentFitnessAndReceptorLogFile.open( bestAgentFitnessAndReceptorLogFilename, std::fstream::app );
        bestAgentFitnessAndReceptorLogFile << std::to_string( seed )  << "," << origFit <<  "," << endl;
        bestAgentFitnessAndReceptorLogFile.close();
      }
      

      //Parameter Mutation Landscape
      //int BEST_SEED=49;
      //if (seed == BEST_SEED ) {
      
      //bias1	bias2	bias3	timConst1	timConst2	timConst3	recep1	recep2	recep3	
      //1		2		3		4			5			6			7		8		9		
      
      //w_1->1	w_1->2	w_1->3	w_2->1	w_2->2	w_2->3	w_3->1	w_3->2	w_3->3  w_AS->1   w_AS->2  w_AS->3 ALL_weights
      //10		11		12		13		14		15		16		17		18      19        20       21      22
      
      std::map <int, string> param_map;
      
      param_map[1] = "bias1";
      param_map[2] = "bias2";
      param_map[3] = "bias3";
      param_map[4] = "timingConst1";
      param_map[5] = "timingConst2";
      param_map[6] = "timingConst3";
      param_map[7] = "recep1";
      param_map[8] = "recep2";
      param_map[9] = "recep3";
      param_map[10] = "w1-to-1";
      param_map[11] = "w1-to-2";
      param_map[12] = "w1-to-3";
      param_map[13] = "w2-to-1";
      param_map[14] = "w2-to-2";
      param_map[15] = "w2-to-3";
      param_map[16] = "w3-to-1";
      param_map[17] = "w3-to-2";
      param_map[18] = "w3-to-3";
      
      param_map[19] = "w_AS-to-1";
      param_map[20] = "w_AS-to-2";
      param_map[21] = "w_AS-to-3";
      
      param_map[22] = "wALL";
      
      param_map[23] = "w*-to-1";
      param_map[24] = "w*-to-2";
      param_map[25] = "w*-to-3";
      param_map[26] = "w*-to-1or2";
      param_map[27] = "w*-to-1or3";
      param_map[28] = "w*-to-2or3";
      
      
      
      
      
      int sliceAMax = stop1;
      int sliceBMax = stop2;
      int sliceAStart = start1;
      int sliceBStart = start2;
      
/////////////////////////// 
      for (int sliceA = sliceAStart; sliceA <= sliceAMax; sliceA++ ) {
        for (int sliceB = sliceBStart; sliceB <= sliceBMax; sliceB++ ) {
          
          if (sliceA != sliceB && sliceA < sliceB) {
          ////////////
            cout << "starting i,j:" << sliceA << "," << sliceB << endl;
            
            string recordMutationsFilename( dirPath  );
            
            //can run and generate plots on all of these
            recordMutationsFilename += "/seed_" + std::to_string( seed ) +"_X-" + param_map[ sliceA ] + "_Y-" + param_map[ sliceB ]+  + "_mutations.csv";
            //recordMutationsFilename += "/seed_" + std::to_string( seed ) + "_mutations.csv";
            
            recordLog.open(  recordMutationsFilename  );
            recordLog << "param1,param2,fitness," << endl;
                  
            cout << "0,0," << origFit << "," << endl;
            
            double min=-1;
            double max=1;
            double inc = 0.01;
            
            for (double i=min; i<max; i+= inc ) {
              cout << "i: " << i << endl;
              for (double j=min; j<max; j+= inc ) {
              
                 //set to exactly
                 if ( abs(i) < inc/10 && abs(j) < inc/10 ) {
                   i=0;
                   j=0;
                 }
                 
                 //could have it return a string with the data below instead?
                 //double mutFit = EvaluateMutants( genome, sliceA, i, sliceB, j );
                 string results = EvaluateMutants( genome, sliceA, i, sliceB, j );
                 recordLog << results << endl;
                 
                 //recordLog << i << "," << j << "," << mutFit << "," << endl;
              }
            }
            
            TVector<double> phenotype(1, genomeSize);
            translate_to_phenotype( genome, phenotype );
            
            if (sliceB == 22 ) {
              //ADD ORIGINAL AT END!
              recordLog << phenotype(sliceA) << "," << 1 << "," << origFit << ",";
            } else {
              //ADD ORIGINAL AT END!
              recordLog << phenotype(sliceA) << "," << phenotype(sliceB) << "," << origFit << ",";
            }
            
            
            
            
            
            recordLog.close();
          /////////////////////  
          }            
          
        }
      }
 /////////////////////////     
      
      cout << "Wrote activity for best agent in seed " << seed  << " to file..." << endl;
      //DONE WRITING GENOME ACTIVITY TO FILE	
  }
  
  cout << "end of func";
  

}

// The main program
int main (int argc, const char* argv[]) {
  
  // This program has three different use cases:
  // 1. generate new data using a particular configuration and storing in a particular directory (experiment name)
  // 2. generate testing data using a directory with genomes inside of it and giving it a label (to be stored inside experiment folder)
  //     A. Would be nice to have a mode where data is written to file and mode where only final values are recorded
  //     B. Would be nice to be able to specify one seed to do this to
  //
  // 3. generate parameter space mutation plots, where different genetic parameters are varied (or all weights shifted)
  
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " CONFIG_FILE.ini  EXPERIMENT_NAME" << std::endl;
    std::cerr << "OR" << std::endl;
    std::cerr << "Usage: " << argv[0] << " CONFIG_FILE.ini GENOME_DIRECTORY LABEL [TRUE OR FALSE]" << std::endl;
    std::cerr << "OR" << std::endl;
    std::cerr << "Usage: " << argv[0] << " CONFIG_FILE.ini GENOME_DIRECTORY LABEL [#] [#] [#] [#]" << std::endl;
    
    return 1;
  }
  
  asprintf(&expName, "%s", argv[2]  );


  char dirPath[200];
  //strcpy( dirPath, "DATA/");
  //strcat(dirPath, expName );
  strcpy( dirPath, expName );
  
  
  
  // Print the user's name:
  cout << "Running experiment "<< argv[2]  <<" according to: " << argv[1] << endl;
  
  //use argument passed in to load from config file
  INIReader reader( argv[1]   );
  if (reader.ParseError() < 0) {
    std::cout << "Can't load '.ini' file!\n";
    return 1;
  }
  
  //load global variable values from reader
  loadValuesFromConfig( reader );
  
  
  // Check the number of parameters
  if (argc >= 4) {
    cout << "Running in Special mode: will generate activity from genomes in directory: " << dirPath << endl;
    
    char* label;
    asprintf(&label, "%s", argv[3]  );
    
    if ( argc >=8 ) {
      cout << "Generating Parameter Space data and will mutate the following: " <<endl;
      cout << "Parameters: " << argv[4] << " " << argv[5] << " " <<argv[6] << " " <<argv[7] << " " << endl;
      //exit(-1);
      cout << "Seed should be: " << startingSeed << endl;
      //exit(-1);
      generateActivityLogsFromGenomes( argv[1], dirPath, label, atoi(argv[4]) , atoi(argv[5]), atoi(argv[6]), atoi(argv[7]) );
      
    } else {
    
    
      cout << "Generating testing data using test file: " << argv[1] << endl;
      generateActivityLogsFromGenomes( argv[1], dirPath, label );
    }
    return -1;
    
  }
  
  strcpy( dirPath, "DATA/");
  strcat(dirPath, expName );
  
  
  //get current date to put in filename
  //time_t secs=time(0);
  //tm *t=localtime(&secs);
  //asprintf(&expName, "%04d-%02d-%02d-%s",t->tm_year+1900,t->tm_mon+1,t->tm_mday,  argv[2]     );


  bool RESTARTING_MODE= dirExists( dirPath ) == 1;
  
  if ( RESTARTING_MODE ) {
        cout << "RESTARTING_MODE!" << endl;
        //INSTEAD DELETE THE LATEST SEED_ACTIVITY LOGS AND START WHERE THEY STOPPED!
        char restart_command[100];
        strcpy( restart_command, ("cd scripts/ && python3 restart.py ") );
        strcat( restart_command, expName );
        //const int restart_err = system( restart_command );

		std::string starting_seed_string = exec( restart_command );
		int orig_starting_seed = startingSeed;
		startingSeed = std::stoi( starting_seed_string );
		int fewer_runs = startingSeed-orig_starting_seed;
		runs = runs - fewer_runs;
        cout << "Starting from seed " << starting_seed_string << " for a total of " << runs << " runs!" << endl;
       
  } else {
        cout << "STARTING NEW EXPERIMENT! Must create directory: " << dirPath << endl;
		char mkdir_command[100];
		strcpy( mkdir_command, ("mkdir -p ") );
	  	strcat( mkdir_command, dirPath );
      	const int dir_err = system( mkdir_command );
      	
		if (-1 == dir_err) {
          printf("Error creating directory!n");
          exit(1);
      	} 
  }


  //******************************************************************
  //     SETTING UP LOGGER FILENAMES 
  //******************************************************************
  string bestAgentGenomeLogFilename( dirPath   );
  bestAgentGenomeLogFilename = bestAgentGenomeLogFilename + "/genomes.txt";
  
  string bestAgentPhenotypeLogFilename( dirPath   );
  bestAgentPhenotypeLogFilename = bestAgentPhenotypeLogFilename + "/phenotypes.txt";
  
  

  string bestAgentFitnessAndReceptorLogFilename( dirPath   );
  bestAgentFitnessAndReceptorLogFilename = bestAgentFitnessAndReceptorLogFilename + "/fitness_and_receptors.txt";

  //******************************************************************
  // START SETUP FROM SCRATCH - must setup HEADERS for CSV
  //******************************************************************
  if ( !RESTARTING_MODE ) {
    
    //Need to open these to write headers
    bestAgentGenomeLogFile.open( bestAgentGenomeLogFilename );  
    bestAgentPhenotypeLogFile.open( bestAgentPhenotypeLogFilename );  
    
    bestAgentFitnessAndReceptorLogFile.open( bestAgentFitnessAndReceptorLogFilename );
    
    
    //Copy config into the destination folder  
    char cp_config_command[100];
    strcpy( cp_config_command, ("cp ") );
    strcat( cp_config_command, argv[1] );
    
    //WHEN STARTING OUT NEED TO COPY THIS
    strcat( cp_config_command, " DATA/" );
    //strcat( cp_config_command, " " );
    strcat( cp_config_command, expName );

    const int cp_err = system( cp_config_command );
    if (-1 == cp_err) {
        printf("Error creating directory!n");
        exit(1);
    }
     
    
    //verify settings are reasonable - true shows info
    cout << "Running tests..." << endl;
    runTests( diplayTestText );
    
    ////////////////////////////////////
    //Setup headers
    bestAgentGenomeLogFile << "seed,";
    cout << "seed," << endl;
    
    for (int i=1; i <= networkSize; i++ ) 
        bestAgentGenomeLogFile << "bias" << i << ",";
    
    for (int i=1; i <= networkSize; i++ ) 
        bestAgentGenomeLogFile << "timConst" << i << ",";
    
    for (int i=1; i <= networkSize; i++ ) 
        bestAgentGenomeLogFile << "recep" << i << ",";
    
    for (int i=1; i <= networkSize; i++ ) { 
      for (int j=1; j <= networkSize; j++ ) {
        bestAgentGenomeLogFile << "w_" << i << "->" << j << ",";   
      } 
    }
    
    for (int i=1; i <= networkSize; i++ ) { 
        bestAgentGenomeLogFile << "w_AS->" << i << ",";   
    }
    
    
    bestAgentGenomeLogFile << endl;
    
    bestAgentFitnessAndReceptorLogFile << "seed,fitness,";
    for (int i=1; i <= networkSize; i++ ) {
      //TODO CHANGE TO PHENO
      bestAgentFitnessAndReceptorLogFile << "r" << i << ",";
    }
    bestAgentFitnessAndReceptorLogFile << endl;
    
    bestAgentFitnessAndReceptorLogFile.close();
    bestAgentGenomeLogFile.close();  
    
    //Setup headers
    bestAgentPhenotypeLogFile << "seed,";
    cout << "seed," << endl;
    
    for (int i=1; i <= networkSize; i++ ) 
        bestAgentPhenotypeLogFile << "bias" << i << ",";
    
    for (int i=1; i <= networkSize; i++ ) 
        bestAgentPhenotypeLogFile << "timConst" << i << ",";
    
    for (int i=1; i <= networkSize; i++ ) 
        bestAgentPhenotypeLogFile << "recep" << i << ",";
    
    for (int i=1; i <= networkSize; i++ ) { 
      for (int j=1; j <= networkSize; j++ ) {
        bestAgentPhenotypeLogFile << "w_" << i << "->" << j << ",";   
      } 
    }
    
    for (int i=1; i <= networkSize; i++ ) { 
      bestAgentPhenotypeLogFile << "w_AS->" << i << ",";   
    }
    
    
    bestAgentPhenotypeLogFile << endl;
    bestAgentPhenotypeLogFile.close();  
    
    

  //*******************************************************
  // STOP SETUP FROM SCRATCH
  //*******************************************************    
    
  } else {
    cout << "Restarting mode!" << endl;
  
  }
  
  
  //******************************************************************************
  //   START RUNNING SIMULATIONS ACCORDING TO SETTINGS LOADED AND LOG APPROPRIATELY
  //******************************************************************************
  
  for ( int i=0; i < runs; i++ ) {
      //let user know how many simulations have been run
      cout << "Simulation with seed #" << std::to_string(startingSeed + i) << " started... ";
      
      //setup seed logfiles
      string seedFilename( dirPath  );
      seedFilename += "/seed_" + std::to_string(startingSeed + i)  + ".txt";
      expLogFile.open(  seedFilename  );
      expLogFile  << "Generation,BestPerf,AvgPerf,PerfVariance" << endl;
      
      //calculate size of vector needed
      TSearch s(  networkSize*neuronParameterCount + networkSize*networkSize   );
      //Use function from above to log to file
      s.SetPopulationStatisticsDisplayFunction( myDisplayFn );
      
      // Configure the search
      s.SetRandomSeed( startingSeed + i );

      s.SetEvaluationFunction(Evaluate);
      s.SetSelectionMode(RANK_BASED);
      s.SetReproductionMode(HILL_CLIMBING);
      s.SetPopulationSize( popSize);
      s.SetMaxGenerations( generations );
      
      //start with 0.5 (per paper results)
      s.SetMutationVariance(0.5);
      
      s.SetCrossoverProbability(0.5);
      s.SetCrossoverMode(TWO_POINT);
      s.SetMaxExpectedOffspring(1.1);
      s.SetElitistFraction(0.1);
      s.SetSearchConstraint(1);
      s.SetCheckpointInterval( 0 );

      // Stage 1 //
      s.SetSearchTerminationFunction(MyTerminationFunction);
      s.ExecuteSearch();
      
      // Stage 2 //
      //set mutaton variance to 0.05per paper results
      s.SetMutationVariance(0.05);
      s.SetSearchTerminationFunction(NULL);
      s.ExecuteSearch();
      
      //ONLY OPEN FILES BETWEEN SUCCESSFUL SEARCHES!
      bestAgentFitnessAndReceptorLogFile.open( bestAgentFitnessAndReceptorLogFilename, std::fstream::app );
      
      bestAgentGenomeLogFile.open( bestAgentGenomeLogFilename, std::fstream::app );  
      // Record seed of individual
      bestAgentGenomeLogFile << (startingSeed + i ) << ",";
      TVector<double> &genome = s.BestIndividual();
      for (int i=1; i <= genome.Size(); i++ ) {
        bestAgentGenomeLogFile << genome[i] << ",";
      }
      bestAgentGenomeLogFile <<  endl;
      /////////////////////
      
      bestAgentPhenotypeLogFile.open( bestAgentPhenotypeLogFilename, std::fstream::app );  
      // Record seed of individual
      bestAgentPhenotypeLogFile << (startingSeed + i ) << ",";
      
      TVector<double> phenotype(1, (networkSize*neuronParameterCount + networkSize*networkSize) );
      
      translate_to_phenotype( s.BestIndividual(), phenotype );
      
      //TVector<double> pheno(1, (networkSize*neuronParameterCount + networkSize*networkSize) );
      
      
      for (int i=1; i <= phenotype.Size(); i++ ) {
        bestAgentPhenotypeLogFile << phenotype[i] << ",";
      }
      bestAgentPhenotypeLogFile <<  endl;
      bestAgentPhenotypeLogFile.close();
      
      
      ////////////////////
      
      bestAgentFitnessAndReceptorLogFile << (startingSeed + i ) << ",";
      bestAgentFitnessAndReceptorLogFile <<   s.BestPerformance() << ",";
      
      //setup csv header for each gene     
      int startingReceptor = 2 * networkSize;
      for (int i=1; i <= networkSize; i++ ) {
          double val = TranslateDoubleToDiscreteValues(   MapSearchParameter(s.BestIndividual()[startingReceptor+i], minReceptor, maxReceptor), discreteLevelsOfModulation );
          bestAgentFitnessAndReceptorLogFile <<  val << "," ;
      }
      bestAgentFitnessAndReceptorLogFile << endl;
      
      expLogFile.close();
      cout << "   complete!" << endl;
      
      //RUN THE BEST AGENT ON THE TASK AT HAND AND RECORD ITS NEURAL ACTIVATIONS AND MOVEMENTS
      string recordFilename( dirPath  );
      recordFilename += "/seed_" + std::to_string(startingSeed + i)  + "_recorded_activity.csv";
      recordLog.open(  recordFilename  );
      
      //evaluate, but record data to specified file
      Evaluate( s.BestIndividual(), recordLog );
      
      recordLog.close();
      
      bestAgentFitnessAndReceptorLogFile.close();
      bestAgentGenomeLogFile.close();  
  
  }      
  //close best agent file
  //bestAgentGenomeLogFile.close();
  //bestAgentFitnessAndReceptorLogFile.close();
  
  return 0;
}


