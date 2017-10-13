// ***************************************************
// An example of Evolving CTRNN controllers for Walkers
// ***************************************************
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
int networkSize;
int neuronParameterCount;
int maxReceptor;
int minReceptor;
double maxModulation;
double minModulation;
bool sinusoidalOscillation;
int externalModulationPeriods;
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
ofstream bestAgentFitnessAndReceptorLogFile;
ofstream recordLog;

//name of experiment as passed in through command argument
char* expName;


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


//*****************************************************
// this version does not log to file
//*****************************************************

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
	return Insect.cx/RunDuration;
}





///**************************************************
// This is the version that records to a log file
//***************************************************
//Evaluate the performance of externally modulated CTRNN controllers with walking task
double Evaluate(TVector<double> &v, ofstream &recordLog)
{
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
    if (recordLog ) {
      recordLog << "time,modulation,jointX,jointY,footX,footY,FootState,cx";
      for (int i=1; i <= networkSize; i++) {
        recordLog << ",n" << i << "_out";
      }
      recordLog << endl;
      
    }

    for (double time = 0; time < RunDuration; time += StepSize) {
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
        if ( recordLog ) {
          recordLog << time << "," << modulationLevel << ",";
          recordLog << Insect.Leg.JointX << "," << Insect.Leg.JointY << ",";
          recordLog << Insect.Leg.FootX << "," << Insect.Leg.FootY << ",";
          recordLog << Insect.Leg.FootState << "," << Insect.cx;
          //write outputs of neurons
          for (int i=1; i <= networkSize; i++) {
            recordLog << "," <<   Insect.NervousSystem.outputs[i]   ;
          }
          recordLog << endl;
        }
    }
	return Insect.cx/RunDuration;
}


//two stage evolution, switching the mutation variance after 0.126 from paper fitness is achieved
int MyTerminationFunction(int Generation,  double BestPerf,  double AvgPerf,  double PerfVar)  {
  if (BestPerf >  Stage1Threshold ) 
      return 1;
  else 
      return 0;
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
      assert( hitTopCount == externalModulationPeriods && externalModulationPeriods == hitBotCount );
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
    
    networkSize                = reader.GetInteger("network","networkSize", 0);
    neuronParameterCount       = reader.GetInteger("network","neuronParameterCount", 3);

    maxReceptor                = reader.GetReal("receptor", "maxReceptor", 1 ); 
    minReceptor                = reader.GetReal("receptor", "minReceptor", -1 );
    discreteLevelsOfModulation = reader.GetInteger("receptor", "discreteLevelsOfModulation", 3 );

    //CHANGE BELOW TO modsignal
    
    maxModulation              = reader.GetReal("modsignal", "maxModulation", 0.5 );
    minModulation              = reader.GetReal("modsignal", "minModulation", -0.5 );
    
    sinusoidalOscillation      = reader.GetBoolean("modsignal", "sinusoidalOscillation", true );
    externalModulationPeriods  = reader.GetInteger("modsignal", "externalModulationPeriods", 2 );
    
    
    
    
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
    
    modulationStepSize =  2 * (maxModulation - minModulation ) *  ( externalModulationPeriods / (RunDuration / StepSize) )  ;
//    cout << "modulationStepSize: " << modulationStepSize << endl;


}


void generateActivityLogsFromGenomes(const char* ini, const char* directory) {
  cout << "inside func" << directory << endl;
  
  //use argument passed in to load from config file
  INIReader reader( ini   );
  
  cout << "trying reader" << endl;
  if (reader.ParseError() < 0) {
    std::cout << "Can't load '.ini' file!\n";
    return;
  }
  
  //load global variable values from reader
  cout <<"trying loadvalues" << endl;
  loadValuesFromConfig( reader );  
  cout << StepSize << " ..";
  
  int genomeSize = (networkSize*neuronParameterCount + networkSize*networkSize);
  
  cout << "TVector of size: " << genomeSize << " must be created!" << endl;

  char genomesFile[100];
  strcpy(genomesFile, directory);
  strcat(genomesFile, "genomes.txt" );
  
  std::ifstream infile( genomesFile );
  
  std::string line;
  bool first=true;
  
  for( std::string line; getline( infile, line ); )  {
      
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
      TVector<double> genome(-1,1);
      genome.SetSize( genomeSize );
      
      istringstream iss( line );
      bool first_val = true;
      int i=0;
      
      do {
        string subs;
        iss >> subs;
        //cout << "sub: " << subs << endl;
        if ( first_val) {
          first_val = false;
          seed = stoi( subs );
          cout << "Seed set to be: " << seed << endl;
        } else {
          i++;
          genome[i] = stof( subs );
          cout << "genome["<<i<<"]: " << genome[i] << endl;
        }
        
      } while (i < genomeSize &&  iss);
      
	
	  string recordFilename( directory  );
      recordFilename += "/seed_" + std::to_string( seed )  + "_recorded_activity.csv";
      
      recordLog.open(  recordFilename  );
      //evaluate, but record data to specified file
      Evaluate(genome,   recordLog );
      
      recordLog.close();
      
      cout << "Wrote activity for best agent in seed " << seed  << " to file..." << endl;
      //DONE WRITING GENOME ACTIVITY TO FILE	
      
      
  }
  


}



// The main program
int main (int argc, const char* argv[]) {
  
  
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " CONFIG_FILE.ini  EXPERIMENT_NAME" << std::endl;
    std::cerr << "OR" << std::endl;
    std::cerr << "Usage: " << argv[0] << " CONFIG_FILE.ini GENOME_DIRECTORY YES" << std::endl;
    return 1;
  }
   
  // Check the number of parameters
  if (argc >= 4) {
    cout << "special mode: generate activity from genomes in directory: " << argv[2] << endl;
    cout << "Do you wish to continue ? (y/n)" << endl;
    char proceed;
    cin >> proceed;
    
    if (proceed == 'y') {
      cout << "Proceeding to generate activity from genomes in directory: " << argv[2] << endl;
      generateActivityLogsFromGenomes( argv[1], argv[2] );
      
      cout << "generateActivityLogsFromGenomes completed..."<<endl;
      
      return -1;
    } else {
      // Tell the user how to run the program
      std::cerr << "Usage: " << argv[0] << " CONFIG_FILE.ini  EXPERIMENT_NAME" << std::endl;
      return 1;
    }
  }
  
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
  
  
  //get current date to put in filename
  time_t secs=time(0);
  tm *t=localtime(&secs);
  asprintf(&expName, "%04d-%02d-%02d-%s",t->tm_year+1900,t->tm_mon+1,t->tm_mday,  argv[2]     );
  

  char dirPath[100];
  strcpy( dirPath, "DATA/");
  strcat(dirPath, expName );
  
  struct stat st;
  if( stat( dirPath  , &st) == 0) {
  
      if(st.st_mode && S_IFDIR != 0) {
        cout << dirPath  <<"  is already present! Exiting...\n";
        exit(1);
      } 
  }
  
  char mkdir_command[100];
  strcpy( mkdir_command, ("mkdir -p ") );
  strcat( mkdir_command, dirPath );
  
  const int dir_err = system( mkdir_command );
  if (-1 == dir_err) {
      printf("Error creating directory!n");
      exit(1);
  } 

  //Copy config into the destination folder  
  char cp_config_command[100];
  strcpy( cp_config_command, ("cp ") );
  strcat( cp_config_command, argv[1] );
  strcat( cp_config_command, " DATA/" );
  strcat( cp_config_command, expName );

  const int cp_err = system( cp_config_command );
  if (-1 == cp_err) {
      printf("Error creating directory!n");
      exit(1);
  }

  
  
   
  
  //verify settings are reasonable - true shows info
  cout << "Running tests..." << endl;
  runTests( diplayTestText );
  
  //******************************************************************
  //     SETTING UP LOGGERS WITH HEADERS AT TOPS OF CSV FILES
  //******************************************************************
  string bestAgentGenomeLogFilename( dirPath   );
  bestAgentGenomeLogFilename = bestAgentGenomeLogFilename + "/genomes.txt";
  bestAgentGenomeLogFile.open( bestAgentGenomeLogFilename );
  
  bestAgentGenomeLogFile << "seed,";
  
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
  bestAgentGenomeLogFile << endl;
  string bestAgentFitnessAndReceptorLogFilename( dirPath   );
  bestAgentFitnessAndReceptorLogFilename = bestAgentFitnessAndReceptorLogFilename + "/fitness_and_receptors.txt";
  bestAgentFitnessAndReceptorLogFile.open( bestAgentFitnessAndReceptorLogFilename );
  bestAgentFitnessAndReceptorLogFile << "seed,fitness,";
  for (int i=1; i <= networkSize; i++ ) {
    bestAgentFitnessAndReceptorLogFile << "r" << i << ",";
  }
  bestAgentFitnessAndReceptorLogFile << endl;
  
  //******************************************************************************
  //   START RUNNING SIMULATIONS ACCORDING TO SETTINGS LOADED AND LOG APPROPRIATELY
  //******************************************************************************
  
  for ( int i=0; i < runs; i++ ) {
      //let user know how many simulations have been run
      cout << "Simulation #" << i << " started... ";
      
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
      s.SetCheckpointInterval(5);
        
      // Stage 1 //
      s.SetSearchTerminationFunction(MyTerminationFunction);
      s.ExecuteSearch();
      
      // Stage 2 //
      //set mutaton variance to 0.05per paper results
      s.SetMutationVariance(0.05);
      s.SetSearchTerminationFunction(NULL);
      s.ExecuteSearch();
      
        
      // Record seed of individual
      bestAgentGenomeLogFile << (startingSeed + i ) << ",";
      TVector<double> &genome = s.BestIndividual();
      for (int i=1; i <= genome.Size(); i++ ) {
        bestAgentGenomeLogFile << genome[i] << ",";
      }
      bestAgentGenomeLogFile <<  endl;
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
  
  
  }      
  //close best agent file
  bestAgentGenomeLogFile.close();
  bestAgentFitnessAndReceptorLogFile.close();
  
  
  //generate plots for directories
  //this should be done as post processing, independent of the simulation running
  
  /*
  //run plot commands!
  char plot_command[100];
  strcpy( plot_command, ("cd ../scripts/plotting/ && python3 csvreader.py ") );
  strcat( plot_command, expName );

  const int plot_err = system( plot_command );
  if (-1 == plot_err) {
      printf("Error running plot command!");
      exit(1);
  }
  */
  
  return 0;
}

